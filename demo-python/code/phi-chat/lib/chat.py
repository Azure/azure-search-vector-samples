from azure.core.credentials_async import AsyncTokenCredential
from azure.identity.aio import get_bearer_token_provider
from azure.search.documents.aio import SearchClient
from azure.search.documents.models import VectorizableTextQuery, HybridSearch
from openai import AsyncAzureOpenAI
import os
from enum import Enum
from typing import List, Optional
import aiohttp

def create_openai_client(credential: AsyncTokenCredential) -> AsyncAzureOpenAI:
    token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")
    return AsyncAzureOpenAI(
        api_version="2024-04-01-preview",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_ad_token_provider=token_provider
    )

def create_search_client(credential: AsyncTokenCredential) -> SearchClient:
    return SearchClient(
        endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        index_name=os.getenv("AZURE_SEARCH_INDEX"),
        credential=credential
    )

class SearchType(Enum):
    TEXT = "text"
    VECTOR = "vector"
    HYBRID = "hybrid"

async def get_sources(search_client: SearchClient, query: str, search_type: SearchType, use_semantic_reranker: bool = True, sources_to_include: int = 5, k: int = 50) -> List[str]:
    if search_type == SearchType.TEXT:
        response = await search_client.search(
            search_text=query,
            query_type="semantic" if use_semantic_reranker else "simple",
            top=sources_to_include,
            select="content,metadata_storage_name"
        )
    elif search_type == SearchType.VECTOR:
        response = await search_client.search(
            search_text="*",
            query_type="simple",
            top=sources_to_include,
            vector_queries=[
                VectorizableTextQuery(text=query, k_nearest_neighbors=k, fields="embedding")
            ],
            semantic_query=query if use_semantic_reranker else None,
            select="content,metadata_storage_name"
        )
    else:
        response = await search_client.search(
            search_text=query,
            query_type="simple",
            top=sources_to_include,
            vector_queries=[
                VectorizableTextQuery(text=query, k_nearest_neighbors=k, fields="embedding")
            ],
            hybrid_search=HybridSearch(
                max_text_recall_size=k
            ),
            semantic_query=query if use_semantic_reranker else None,
            select="content,metadata_storage_name"
        )

    return [ document async for document in response ]

GROUNDED_PROMPT="""
Answer the query using only the sources provided below.
Answer ONLY with the facts listed in the list of sources below. If there isn't enough information below, say you don't know. Do not generate answers that don't use the sources below. If asking a clarifying question to the user would help, ask the question.
Each source has a name followed by colon and the actual information, always include the source name for each fact you use in the response. Use square brackets to reference the source, for example [info1.txt]. Don't combine sources, list each source separately, for example [info1.txt][info2.pdf].
Query: {query}
Sources:\n{sources}
"""
class ChatThread:
    def __init__(self):
        self.messages = []
        self.search_results = []
    
    def append_message(self, role: str, message: str):
        self.messages.append({
            "role": role,
            "content": message
        })

    async def append_grounded_message(self, search_client: SearchClient, query: str, search_type: SearchType, use_semantic_reranker: bool = True, sources_to_include: int = 5, k: int = 50):
        sources = await get_sources(search_client, query, search_type, use_semantic_reranker, sources_to_include, k)
        sources_formatted = "\n".join([f'{document["metadata_storage_name"]}:{document["content"]}' for document in sources])
        self.append_message(role="user", message=GROUNDED_PROMPT.format(query=query, sources=sources_formatted))
        self.search_results.append(
            {
                "message_index": len(self.messages) - 1,
                "query": query,
                "sources": sources
            }
        )

    async def get_openai_response(self, openai_client: AsyncAzureOpenAI, model: str):
        response = await openai_client.chat.completions.create(
            messages=self.messages,
            model=model
        )
        self.append_message(role="assistant", message=response.choices[0].message.content)

    async def get_phi3_response(self, endpoint_scoring_uri: str, endpoint_authorization: str, deployment: str, temperature: float = 0.7, top_p: float = 0.9, do_sample: bool = True, max_new_tokens: int = 128):
        headers = {
            "Authorization": endpoint_authorization,
            "azureml-model-deployment": deployment
        }
        body = {
            "input_data": {
                "input_string": self.messages,
                "parameters": {
                    "temperature": temperature,
                    "top_p": top_p,
                    "do_sample": do_sample,
                    "max_new_tokens": max_new_tokens
                }
            }
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url=endpoint_scoring_uri, headers=headers, json=body) as response:
                response.raise_for_status()
                response_body = await response.json()
                self.append_message(role="assistant", message=response_body["output"])

    def get_last_message(self) -> Optional[object]:
        return self.messages[-1] if len(self.messages) > 0 else None

    def get_last_message_sources(self) -> Optional[List[object]]:
        return self.search_results[-1]["sources"] if len(self.search_results) > 0 else None