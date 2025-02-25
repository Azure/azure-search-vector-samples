from importlib import reload
import langchain_community.vectorstores.azuresearch
from typing import Callable, Optional, List
import os
from azure.search.documents.indexes import SearchIndexerClient, SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    HnswParameters,
    VectorSearchProfile,
    AzureOpenAIVectorizer,
    AzureOpenAIParameters,
    SearchIndex,
    NativeBlobSoftDeleteDeletionDetectionPolicy,
    SemanticConfiguration,
    SemanticSearch,
    SemanticPrioritizedFields,
    SemanticField,
    SplitSkill,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    AzureOpenAIEmbeddingSkill,
    SearchIndexerIndexProjections,
    SearchIndexerIndexProjectionSelector,
    SearchIndexerIndexProjectionsParameters,
    IndexProjectionMode,
    SearchIndexerSkillset,
    SearchIndexer,
    FieldMapping,
    IndexingSchedule
)
from datetime import timedelta
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from azure.storage.blob import BlobServiceClient  
import os
import glob

def upload_sample_documents(
        blob_connection_string: str,
        blob_container_name: str,
        use_user_identity: bool = True
    ):
    # Connect to Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string(conn_str=blob_connection_string, credential=DefaultAzureCredential() if use_user_identity else None)
    container_client = blob_service_client.get_container_client(blob_container_name)
    if not container_client.exists():
        container_client.create_container()

    documents_directory = os.path.join("..", "..", "..", "..", "data", "benefitdocs")
    pdf_files = glob.glob(os.path.join(documents_directory, '*.pdf'))
    for file in pdf_files:
        with open(file, "rb") as data:
            name = os.path.basename(file)
            if not container_client.get_blob_client(name).exists():
                container_client.upload_blob(name=name, data=data)

def create_sample_datasource(
        indexer_client: SearchIndexerClient,
        blob_container_name: str,
        index_name: str,
        search_blob_connection_string: str):
    # Create a data source 
    container = SearchIndexerDataContainer(name=blob_container_name)
    data_source_connection = SearchIndexerDataSourceConnection(
        name=f"{index_name}-blob",
        type="azureblob",
        connection_string=search_blob_connection_string,
        container=container,
        data_deletion_detection_policy=NativeBlobSoftDeleteDeletionDetectionPolicy()
    )
    return indexer_client.create_or_update_data_source_connection(data_source_connection)

def create_sample_index(
        index_client: SearchIndexClient,
        index_name: str,
        azure_openai_endpoint: str,
        azure_openai_ada002_embedding_deployment: str,
        azure_openai_3_large_embedding_deployment: str,
        azure_openai_key: Optional[str] = None
    ):
    # Create a search index  
    fields = [  
        SearchField(name="parent_id", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),  
        SearchField(name="title", type=SearchFieldDataType.String),  
        SearchField(name="chunk_id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True, facetable=True, analyzer_name="keyword"),  
        SearchField(name="chunk", type=SearchFieldDataType.String, sortable=False, filterable=False, facetable=False),  
        SearchField(name="vector_ada002", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), vector_search_dimensions=1536, vector_search_profile_name="hnsw_ada002"),
        SearchField(name="vector_3_large", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), vector_search_dimensions=3072, vector_search_profile_name="hnsw_3_large")
    ]  
  
    # Configure the vector search configuration  
    vector_search = VectorSearch(  
        algorithms=[  
            HnswAlgorithmConfiguration(  
                name="hnsw",  
                parameters=HnswParameters()
            )
        ],  
        profiles=[  
            VectorSearchProfile(  
                name="hnsw_ada002",  
                algorithm_configuration_name="hnsw",  
                vectorizer="ada002",  
            ),
            VectorSearchProfile(  
                name="hnsw_3_large",  
                algorithm_configuration_name="hnsw",  
                vectorizer="3_large",  
            ),
        ],  
        vectorizers=[  
            AzureOpenAIVectorizer(  
                name="ada002",  
                kind="azureOpenAI",  
                azure_open_ai_parameters=AzureOpenAIParameters(  
                    resource_uri=azure_openai_endpoint,  
                    deployment_id=azure_openai_ada002_embedding_deployment,  
                    api_key=azure_openai_key,
                    model_name="text-embedding-ada-002"
                )
            ),
            AzureOpenAIVectorizer(  
                name="3_large",  
                kind="azureOpenAI",  
                azure_open_ai_parameters=AzureOpenAIParameters(  
                    resource_uri=azure_openai_endpoint,  
                    deployment_id=azure_openai_3_large_embedding_deployment,  
                    api_key=azure_openai_key,
                    model_name="text-embedding-3-large"
                )
            )  
        ],  
    )

    semantic_config = SemanticConfiguration(  
        name="my-semantic-config",  
        prioritized_fields=SemanticPrioritizedFields(  
            content_fields=[SemanticField(field_name="chunk")]  
        ))

    # Create the semantic search with the configuration  
    semantic_search = SemanticSearch(configurations=[semantic_config])  

    # Create the search index
    index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search, semantic_search=semantic_search)  
    return index_client.create_or_update_index(index)  

def create_sample_skillset(
        search_indexer_client: SearchIndexerClient,
        index_name: str,
        azure_openai_endpoint: str,
        azure_openai_ada002_embedding_deployment: str,
        azure_openai_3_large_embedding_deployment: str,
        azure_openai_key: Optional[str] = None
    ):
    # Create a skillset  
    skillset_name = f"{index_name}-skillset"  
    
    split_skill = SplitSkill(  
        description="Split skill to chunk documents",  
        text_split_mode="pages",  
        context="/document",  
        maximum_page_length=2000,  
        page_overlap_length=500,  
        inputs=[  
            InputFieldMappingEntry(name="text", source="/document/content"),  
        ],  
        outputs=[  
            OutputFieldMappingEntry(name="textItems", target_name="pages")  
        ],  
    )  
    
    embedding_ada_002_skill = AzureOpenAIEmbeddingSkill(  
        description="Skill to generate ada 002 embeddings via Azure OpenAI",  
        context="/document/pages/*",  
        resource_uri=azure_openai_endpoint,  
        deployment_id=azure_openai_ada002_embedding_deployment,  
        api_key=azure_openai_key,
        model_name="text-embedding-ada-002",
        inputs=[  
            InputFieldMappingEntry(name="text", source="/document/pages/*"),  
        ],  
        outputs=[  
            OutputFieldMappingEntry(name="embedding", target_name="vector_ada002")  
        ],  
    )

    embedding_3_large_skill = AzureOpenAIEmbeddingSkill(  
        description="Skill to generate ada 002 embeddings via Azure OpenAI",  
        context="/document/pages/*",  
        resource_uri=azure_openai_endpoint,  
        deployment_id=azure_openai_3_large_embedding_deployment,  
        api_key=azure_openai_key,
        model_name="text-embedding-3-large",
        inputs=[  
            InputFieldMappingEntry(name="text", source="/document/pages/*"),  
        ],  
        outputs=[  
            OutputFieldMappingEntry(name="embedding", target_name="vector_3_large")  
        ],  
    )  
    
    index_projections = SearchIndexerIndexProjections(  
        selectors=[  
            SearchIndexerIndexProjectionSelector(  
                target_index_name=index_name,  
                parent_key_field_name="parent_id",  
                source_context="/document/pages/*",  
                mappings=[  
                    InputFieldMappingEntry(name="chunk", source="/document/pages/*"),  
                    InputFieldMappingEntry(name="vector_ada002", source="/document/pages/*/vector_ada002"),
                    InputFieldMappingEntry(name="vector_3_large", source="/document/pages/*/vector_3_large"),
                    InputFieldMappingEntry(name="title", source="/document/metadata_storage_name"),  
                ],  
            ),  
        ],  
        parameters=SearchIndexerIndexProjectionsParameters(  
            projection_mode=IndexProjectionMode.SKIP_INDEXING_PARENT_DOCUMENTS  
        ),  
    )  
    
    skillset = SearchIndexerSkillset(  
        name=skillset_name,  
        description="Skillset to chunk documents and generating embeddings",  
        skills=[split_skill, embedding_3_large_skill, embedding_ada_002_skill],  
        index_projections=index_projections,  
    )  
    
    return search_indexer_client.create_or_update_skillset(skillset)  

def create_sample_indexer(
        search_indexer_client: SearchIndexerClient,
        index_name: str,
        skilset_name: str,
        datasource_name: str
    ):
    # Create an indexer  
    indexer_name = f"{index_name}-indexer"  
    
    indexer = SearchIndexer(  
        name=indexer_name,  
        description="Indexer to index documents and generate embeddings",  
        skillset_name=skilset_name,  
        target_index_name=index_name,  
        data_source_name=datasource_name,  
        # Map the metadata_storage_name field to the title field in the index to display the PDF title in the search results  
        field_mappings=[FieldMapping(source_field_name="metadata_storage_name", target_field_name="title")],
        schedule=IndexingSchedule(interval=timedelta(minutes=5))
    )  
    
    indexer = search_indexer_client.create_or_update_indexer(indexer)  
    
    # Run the indexer  
    search_indexer_client.run_indexer(indexer_name)
    return indexer

def create_langchain_azure_openai_wrappers(
        azure_openai_api_version: str,
        azure_openai_endpoint: str,
        azure_openai_3_large_embedding_deployment: str,
        azure_openai_ada002_embedding_deployment: str,
        azure_openai_generator_deployment: str,
        azure_openai_critic_deployment: str,
        azure_openai_key: Optional[str] = None
    ):
    openai_credential = DefaultAzureCredential()
    token_provider = get_bearer_token_provider(openai_credential, "https://cognitiveservices.azure.com/.default")

    azure_openai_args = {
        "openai_api_version": azure_openai_api_version,
        "azure_endpoint": azure_openai_endpoint,
        "api_key": azure_openai_key,
        "azure_ad_token_provider": token_provider if not azure_openai_key else None
    }

    # Use API key if provided, otherwise use RBAC authentication
    text_3_large_embeddings = AzureOpenAIEmbeddings(
        azure_deployment=azure_openai_3_large_embedding_deployment,
        **azure_openai_args
    )
    ada_002_embeddings = AzureOpenAIEmbeddings(
        azure_deployment=azure_openai_ada002_embedding_deployment,
        **azure_openai_args
    )

    generator_llm = AzureChatOpenAI(
        azure_deployment=azure_openai_generator_deployment,
        **azure_openai_args
    )

    critic_llm = AzureChatOpenAI(
        azure_deployment=azure_openai_critic_deployment,
        **azure_openai_args
    )
    return (text_3_large_embeddings, ada_002_embeddings, generator_llm, critic_llm)

def create_langchain_vectorstore(
        azure_search_endpoint: str,
        azure_search_key: str,
        index_name: str,
        embedding_function: Callable,
        search_type: str = "semantic_hybrid",
        vector_field_name: Optional[str] = None):
    os.environ["AZURESEARCH_FIELDS_CONTENT_VECTOR"] = vector_field_name
    os.environ["AZURESEARCH_FIELDS_CONTENT"] = "chunk"
    reload(langchain_community.vectorstores.azuresearch)

    return langchain_community.vectorstores.azuresearch.AzureSearch(
        azure_search_endpoint=azure_search_endpoint,
        azure_search_key=azure_search_key,
        index_name=index_name,
        embedding_function=embedding_function,
        search_type=search_type
    )
