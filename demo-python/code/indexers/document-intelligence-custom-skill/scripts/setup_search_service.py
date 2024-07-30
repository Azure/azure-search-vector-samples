from azure.core.exceptions import ResourceNotFoundError
from azure.core.pipeline.policies import HTTPPolicy
from azure.identity import DefaultAzureCredential
from azure.mgmt.web import WebSiteManagementClient
from azure.storage.blob import BlobServiceClient
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import (
    AzureOpenAIParameters,  
    AzureOpenAIVectorizer,
    SearchField,
    SearchFieldDataType,
    HnswAlgorithmConfiguration,
    VectorSearch,
    VectorSearchProfile,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    SearchIndexerDataSourceConnection,
    SearchIndexerDataContainer,
    SplitSkill,
    SearchIndexer,
    WebApiSkill,
    AzureOpenAIEmbeddingSkill,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    FieldMapping,
    IndexProjectionMode,
    SearchIndexerIndexProjectionSelector,  
    SearchIndexerIndexProjections,  
    SearchIndexerIndexProjectionsParameters, 
    SearchIndexerSkillset
)
import os
from tenacity import (
    Retrying,
    retry_if_exception_type,
    wait_random_exponential,
    stop_after_attempt
)

function_name = "GetTextEmbedding"
sample_index_name = "document-intelligence-index"
sample_container_name = "document-intelligence-sample-data"
sample_datasource_name = "document-intelligence-datasource"
sample_skillset_name = "document-intelligence-skillset"
sample_indexer_name = "document-intelligence-indexer"

def main():
    credential = DefaultAzureCredential()
    search_service_name = os.environ["AZURE_SEARCH_SERVICE"]
    search_url = f"https://{search_service_name}.search.windows.net"
    search_index_client = SearchIndexClient(endpoint=search_url, credential=credential)
    search_indexer_client = SearchIndexerClient(endpoint=search_url, credential=credential)

    print("Uploading sample data...")
    upload_sample_data(credential)

    print("Getting function URL...")
    function_url = get_function_url(credential)

    print(f"Create or update sample index {sample_index_name}...")
    create_or_update_sample_index(search_index_client, function_url)

    print(f"Create or update sample data source {sample_datasource_name}...")
    create_or_update_datasource(search_indexer_client)

    print(f"Create or update sample skillset {sample_skillset_name}")
    create_or_update_skillset(search_indexer_client, function_url)

    print(f"Create or update sample indexer {sample_indexer_name}")
    create_or_update_indexer(search_indexer_client)

def get_function_url(credential: DefaultAzureCredential) -> str:
    subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
    client = WebSiteManagementClient(credential=credential, subscription_id=subscription_id)

    resource_group = os.environ["AZURE_API_SERVICE_RESOURCE_GROUP"]
    function_app_name = os.environ["AZURE_API_SERVICE"]
    # It's possible the function is not fully provisioned by the time this script runs
    # Retry fetching the function information a few times before giving up if it's not found
    for attempt in Retrying(
        retry=retry_if_exception_type(ResourceNotFoundError),
        wait=wait_random_exponential(min=15, max=60),
        stop=stop_after_attempt(5)
    ):
        with attempt:
            embedding_function = client.web_apps.get_function(resource_group_name=resource_group, name=function_app_name, function_name=function_name)
            embedding_function_keys = client.web_apps.list_function_keys(resource_group_name=resource_group, name=function_app_name, function_name=function_name)
            function_url_template = embedding_function.invoke_url_template
            function_key = embedding_function_keys.additional_properties["default"]
            return f"{function_url_template}?code={function_key}"

def upload_sample_data(credential: DefaultAzureCredential):
    # Connect to Blob Storage
    account_url = os.environ["AZURE_STORAGE_ACCOUNT_BLOB_URL"]
    blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)
    container_client = blob_service_client.get_container_client(sample_container_name)
    if not container_client.exists():
        container_client.create_container()
    sample_data_directory_name = os.path.join("..", "..", "data", "documents")
    sample_data_directory = os.path.join(os.getcwd(), sample_data_directory_name)
    for filename in os.listdir(sample_data_directory):
        with open(os.path.join(sample_data_directory, filename), "rb") as f:
            blob_client = container_client.get_blob_client(filename)
            if not blob_client.exists():
                print(f"Uploading {filename}...")
                blob_client.upload_blob(data=f)

def create_or_update_sample_index(search_index_client: SearchIndexClient, custom_vectorizer_url: str):
    vector_dimensions = os.environ["AZURE_OPENAI_EMB_DIMENSIONS"]
    # Create a search index  
    fields = [  
        SearchField(name="parent_id", type=SearchFieldDataType.String, sortable=True, filterable=True, facetable=True),  
        SearchField(name="title", type=SearchFieldDataType.String),  
        SearchField(name="chunk_id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True, facetable=True, analyzer_name="keyword"),  
        SearchField(name="chunk", type=SearchFieldDataType.String, sortable=False, filterable=False, facetable=False),  
        SearchField(name="vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), vector_search_dimensions=vector_dimensions, vector_search_profile_name="hnswProfile"),  
    ]  
    
    vectorizer_resource_uri = os.environ["AZURE_OPENAI_ENDPOINT"]
    vectorizer_deployment = os.environ["AZURE_OPENAI_EMB_DEPLOYMENT"]
    vectorizer_model = os.environ["AZURE_OPENAI_EMB_MODEL"]
    # Configure the vector search configuration  
    vector_search = VectorSearch(  
        algorithms=[  
            HnswAlgorithmConfiguration(  
                name="hnsw"
            )
        ],  
        profiles=[  
            VectorSearchProfile(  
                name="hnswProfile",  
                algorithm_configuration_name="hnsw",  
                vectorizer="vectorizer",  
            )
        ],  
        vectorizers=[  
            AzureOpenAIVectorizer(
                name="vectorizer",
                azure_open_ai_parameters=AzureOpenAIParameters(
                    resource_uri=vectorizer_resource_uri,
                    deployment_id=vectorizer_deployment,
                    model_name=vectorizer_model
                )
            )
        ]
    )  
    
    semantic_config = SemanticConfiguration(  
        name="my-semantic-config",  
        prioritized_fields=SemanticPrioritizedFields(  
            content_fields=[SemanticField(field_name="chunk")]  
        ),  
    )  
    
    # Create the semantic settings with the configuration  
    semantic_search = SemanticSearch(configurations=[semantic_config])

    # Create the search index with the semantic settings  
    index = SearchIndex(name=sample_index_name, fields=fields, vector_search=vector_search, semantic_search=semantic_search)  
    search_index_client.create_or_update_index(index)  

def create_or_update_datasource(search_indexer_client: SearchIndexerClient):
    storage_resource_id = os.environ["AZURE_STORAGE_ACCOUNT_ID"]
    data_source = SearchIndexerDataSourceConnection(
        name=sample_datasource_name,
        type="azureblob",
        connection_string=f"ResourceId={storage_resource_id};",
        container=SearchIndexerDataContainer(name=sample_container_name))
    search_indexer_client.create_or_update_data_source_connection(data_source)

def create_or_update_skillset(search_indexer_client: SearchIndexerClient, document_skill_url: str):
    document_skill = WebApiSkill(
        description="Document intelligence skill to extract content from documents",
        context="/document",
        uri=document_skill_url,
        inputs=[
            InputFieldMappingEntry(name="file_data", source="/document/file_data")
        ],
        outputs=[
            OutputFieldMappingEntry(name="content", target_name="file_content")
        ]
    )

    split_skill = SplitSkill(  
        description="Split skill to chunk documents",  
        text_split_mode="pages",  
        context="/document",  
        maximum_page_length=300,  
        page_overlap_length=20,  
        inputs=[  
            InputFieldMappingEntry(name="text", source="/document/file_content"),  
        ],  
        outputs=[  
            OutputFieldMappingEntry(name="textItems", target_name="pages")  
        ],  
    )  

    vectorizer_resource_uri = os.environ["AZURE_OPENAI_ENDPOINT"]
    vectorizer_deployment = os.environ["AZURE_OPENAI_EMB_DEPLOYMENT"]
    vectorizer_model = os.environ["AZURE_OPENAI_EMB_MODEL"]
    embedding_skill = AzureOpenAIEmbeddingSkill(  
        description="Skill to generate embeddings via a custom endpoint",  
        context="/document/pages/*",
        resource_uri=vectorizer_resource_uri,
        deployment_id=vectorizer_deployment,
        model_name=vectorizer_model,
        inputs=[
            InputFieldMappingEntry(name="text", source="/document/pages/*"),  
        ],  
        outputs=[  
            OutputFieldMappingEntry(name="embedding", target_name="vector")  
        ]
    )
    
    index_projections = SearchIndexerIndexProjections(  
        selectors=[  
            SearchIndexerIndexProjectionSelector(  
                target_index_name=sample_index_name,  
                parent_key_field_name="parent_id",  
                source_context="/document/pages/*",  
                mappings=[  
                    InputFieldMappingEntry(name="chunk", source="/document/pages/*"),  
                    InputFieldMappingEntry(name="vector", source="/document/pages/*/vector"),  
                    InputFieldMappingEntry(name="title", source="/document/metadata_storage_name"),  
                ],  
            ),  
        ],  
        parameters=SearchIndexerIndexProjectionsParameters(  
            projection_mode=IndexProjectionMode.SKIP_INDEXING_PARENT_DOCUMENTS  
        ),
    )  
    
    skillset = SearchIndexerSkillset(  
        name=sample_skillset_name,  
        description="Skillset to use document intelligence, chunk documents and generating embeddings",  
        skills=[split_skill, embedding_skill],  
        index_projections=index_projections,  
    )
    result = search_indexer_client.create_or_update_skillset(skillset)

def create_or_update_indexer(search_indexer_client: SearchIndexerClient):
    indexer = SearchIndexer(  
        name=sample_indexer_name,  
        description="Indexer to index documents and generate embeddings",  
        skillset_name=sample_skillset_name,  
        target_index_name=sample_index_name,  
        data_source_name=sample_datasource_name,  
        # Map the metadata_storage_name field to the title field in the index to display the PDF title in the search results  
        field_mappings=[FieldMapping(source_field_name="metadata_storage_name", target_field_name="title")]  
    )  
    
    search_indexer_client.create_or_update_indexer(indexer)  

if __name__ == "__main__":
    main()