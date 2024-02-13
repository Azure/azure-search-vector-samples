from azure.search.documents import SearchClient
from azure.search.documents.models import (
    VectorizedQuery,
    QueryType,
    QueryCaptionType,
    QueryAnswerType
)
from langchain_core.documents import Document
from langchain_community.vectorstores.azuresearch import (
    AzureSearch,
    FIELDS_CONTENT_VECTOR,
    FIELDS_CONTENT,
    FIELDS_ID,
    FIELDS_METADATA
)
from typing import Optional, List, Tuple, Any
import numpy as np
import json

def vector_search_with_score(
    self, query: str = "", k: int = 4, filters: Optional[str] = None
) -> List[Tuple[Document, float]]:
    """Return docs most similar to query.

    Args:
        query: Text to look up documents similar to.
        k: Number of Documents to return. Defaults to 4.

    Returns:
        List of Documents most similar to the query and score for each
    """

    results = self.client.search(
        search_text="",
        vector_queries=[
            VectorizedQuery(
                vector=np.array(self.embed_query(query), dtype=np.float32).tolist(),
                k_nearest_neighbors=k,
                fields=FIELDS_CONTENT_VECTOR,
            )
        ],
        filter=filters,
    )
    # Convert results to Document objects
    docs = [
        (
            Document(
                page_content=result.pop(FIELDS_CONTENT),
                metadata={
                    **(
                        {FIELDS_ID: result.pop(FIELDS_ID)}
                        if FIELDS_ID in result
                        else {}
                    ),
                    **(
                        json.loads(result[FIELDS_METADATA])
                        if FIELDS_METADATA in result
                        else {
                            k: v
                            for k, v in result.items()
                            if k != FIELDS_CONTENT_VECTOR
                        }
                    ),
                },
            ),
            float(result["@search.score"]),
        )
        for result in results
    ]
    return docs


def hybrid_search_with_score(
    self, query: str = "", k: int = 4, filters: Optional[str] = None
) -> List[Tuple[Document, float]]:
    """Return docs most similar to query with an hybrid query.

    Args:
        query: Text to look up documents similar to.
        k: Number of Documents to return. Defaults to 4.

    Returns:
        List of Documents most similar to the query and score for each
    """

    results = self.client.search(
        search_text=query,
        vector_queries=[
            VectorizedQuery(
                vector=np.array(self.embed_query(query), dtype=np.float32).tolist(),
                k_nearest_neighbors=k,
                fields=FIELDS_CONTENT_VECTOR,
            )
        ],
        filter=filters,
        top=k,
    )
    # Convert results to Document objects
    docs = [
        (
            Document(
                page_content=result.pop(FIELDS_CONTENT),
                metadata={
                    **(
                        {FIELDS_ID: result.pop(FIELDS_ID)}
                        if FIELDS_ID in result
                        else {}
                    ),
                    **(
                        json.loads(result[FIELDS_METADATA])
                        if FIELDS_METADATA in result
                        else {
                            k: v
                            for k, v in result.items()
                            if k != FIELDS_CONTENT_VECTOR
                        }
                    ),
                },
            ),
            float(result["@search.score"]),
        )
        for result in results
    ]
    return docs

def semantic_hybrid_search_with_score_and_rerank(
    self, query: str = "", k: int = 4, filters: Optional[str] = None
) -> List[Tuple[Document, float, float]]:
    """Return docs most similar to query with an hybrid query.

    Args:
        query: Text to look up documents similar to.
        k: Number of Documents to return. Defaults to 4.

    Returns:
        List of Documents most similar to the query and score for each
    """

    results = self.client.search(
        search_text=query,
        vector_queries=[
            VectorizedQuery(
                vector=np.array(self.embed_query(query), dtype=np.float32).tolist(),
                k_nearest_neighbors=50,
                fields=FIELDS_CONTENT_VECTOR,
            )
        ],
        filter=filters,
        query_type=QueryType.SEMANTIC,
        semantic_configuration_name=self.semantic_configuration_name,
        query_caption=QueryCaptionType.EXTRACTIVE,
        query_answer=QueryAnswerType.EXTRACTIVE,
        top=k,
    )
    # Get Semantic Answers
    semantic_answers = results.get_answers() or []
    semantic_answers_dict = {}
    for semantic_answer in semantic_answers:
        semantic_answers_dict[semantic_answer.key] = {
            "text": semantic_answer.text,
            "highlights": semantic_answer.highlights,
        }
    # Convert results to Document objects
    docs = [
        (
            Document(
                page_content=result.pop(FIELDS_CONTENT),
                metadata={
                    **(
                        {FIELDS_ID: result.pop(FIELDS_ID)}
                        if FIELDS_ID in result
                        else {}
                    ),
                    **(
                        json.loads(result[FIELDS_METADATA])
                        if FIELDS_METADATA in result
                        else {
                            k: v
                            for k, v in result.items()
                            if k != FIELDS_CONTENT_VECTOR
                        }
                    ),
                    **{
                        "captions": {
                            "text": result.get("@search.captions", [{}])[0].text,
                            "highlights": result.get("@search.captions", [{}])[
                                0
                            ].highlights,
                        }
                        if result.get("@search.captions")
                        else {},
                        "answers": semantic_answers_dict.get(
                            json.loads(result[FIELDS_METADATA]).get("key")
                            if FIELDS_METADATA in result
                            else "",
                            "",
                        ),
                    },
                },
            ),
            float(result["@search.score"]),
            float(result["@search.reranker_score"]),
        )
        for result in results
    ]
    return docs

def fix_vectorstore(store: AzureSearch):
    store.vector_search_with_score = vector_search_with_score.__get__(store, store.__class__)
    store.hybrid_search_with_score = hybrid_search_with_score.__get__(store, store.__class__)
    store.semantic_hybrid_search_with_score_and_rerank = semantic_hybrid_search_with_score_and_rerank.__get__(store, store.__class__)