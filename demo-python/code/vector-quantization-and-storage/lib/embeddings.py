from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import os
import json

file_directory = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(
    file_directory,
    "..",
    "..",
    "..",
    "data",
    "documents")
content_path = os.path.join(
    file_directory,
    "..",
    "..",
    "..",
    "..",
    "data",
    "documentVectors.json")

# You can create the index used by this function using the integrated vectorization notebook
def load_chunks_from_index():
    load_dotenv(override=True)
    endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
    key = os.getenv("AZURE_SEARCH_ADMIN_KEY")
    index = os.getenv("AZURE_SEARCH_INDEX")
    search_client = SearchClient(endpoint, index, AzureKeyCredential(key))
    content = []
    for doc in search_client.search(search_text="", top=1000, select="chunk_id,chunk,title"):
        content.append({"id": doc["chunk_id"], "chunk": doc["chunk"], "title": doc["title"], "embedding": doc["vector"]})
    with open(content_path, "w") as f:
        json.dump(content, f)

# Optionally re-embed all the chunks
# Can be used to test a different embedding model such as text-embedding-3-large
def create_embeddings():
    load_dotenv(override=True)
    openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    openai_key = os.getenv("AZURE_OPENAI_KEY")
    embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    embedding_dimensions = int(os.getenv("AZURE_OPENAI_EMBEDDING_DIMENSIONS", 1536))
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")

    openai_credential = DefaultAzureCredential()
    token_provider = get_bearer_token_provider(openai_credential, "https://cognitiveservices.azure.com/.default")

    client = AzureOpenAI(
        api_version=api_version,
        azure_endpoint=openai_endpoint,
        api_key=openai_key,
        azure_ad_token_provider=token_provider if not openai_key else None
    )
    
    with open(content_path, "rb") as f:
        content = json.load(f)
    chunks = [c["chunk"] for c in content]
    embedding_response = client.embeddings.create(input=chunks, model=embedding_deployment, dimensions=embedding_dimensions)
    embeddings = [item.embedding for item in embedding_response.data]
    for item, embedding in zip(content, embeddings):
        item["embedding"] = embedding
    
    with open(content_path, "w") as f:
        json.dump(content, f)
