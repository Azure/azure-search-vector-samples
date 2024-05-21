import asyncio
from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient
from azure.search.documents.indexes.aio import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchIndexerSkillset,
    SearchIndexer,
    SearchIndexerDataSourceConnection,
    SearchIndexerDataContainer,
    SearchIndexerDataSourceType,
    SearchIndexerIndexProjections,
    SearchIndexerIndexProjectionSelector,
    SearchIndexerIndexProjectionsParameters,
    IndexProjectionMode,
    AzureOpenAIEmbeddingSkill,
    SplitSkill,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    SearchFieldDataType,
    ScalarQuantizationCompressionConfiguration,
    VectorSearchProfile,
    VectorSearch,
    SearchField,
    SearchableField,
    SimpleField,
    AzureOpenAIVectorizer,
    AzureOpenAIParameters,
    HnswAlgorithmConfiguration,
    LexicalAnalyzerName,
    SemanticSearch,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields
)
import os
import glob

current_file_directory = os.path.dirname(os.path.abspath(__file__))
samples_path = os.path.join(current_file_directory, "..", "..", "..", "data", "documents")

async def main():
    async with DefaultAzureCredential() as credential:
        print("Uploading sample documents...")
        blob_url = os.getenv("AZURE_STORAGE_ACCOUNT_BLOB_URL")
        async with BlobServiceClient(account_url=blob_url, credential=credential) as blob_service_client:
            await upload_documents(blob_service_client)

        print("Creating index...")
        search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        async with SearchIndexClient(endpoint=search_endpoint, credential=credential) as search_index_client:
            await create_index(search_index_client)
        
        async with SearchIndexerClient(endpoint=search_endpoint, credential=credential) as search_indexer_client:
            print("Creating skillset...")
            await create_skillset(search_indexer_client)
            print("Creating datasource...")
            await create_datasource(search_indexer_client)
            print("Creating indexer...")
            await create_indexer(search_indexer_client)

        print("Done")

async def upload_documents(blob_service_client: BlobServiceClient):
    container_client = blob_service_client.get_container_client(os.getenv("AZURE_STORAGE_CONTAINER"))
    image_paths = glob.glob(os.path.join(samples_path, "*.pdf"))
    for image_path in image_paths:
        async with container_client.get_blob_client(os.path.basename(image_path)) as blob_client:
            if not await blob_client.exists():
                with open(image_path, "rb") as data:
                    await blob_client.upload_blob(data=data)

async def create_index(search_index_client: SearchIndexClient):
    index = SearchIndex(
        name=os.getenv("AZURE_SEARCH_INDEX"),
        fields=[
            SearchableField(
                name="id",
                type=SearchFieldDataType.String,
                key=True,
                filterable=True,
                analyzer_name=LexicalAnalyzerName.KEYWORD
            ),
            SearchableField(
                name="document_id",
                type=SearchFieldDataType.String,
                key=False,
                filterable=True,
                analyzer_name=LexicalAnalyzerName.KEYWORD
            ),
            SearchField(
                name="embedding",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                stored=False,
                vector_search_dimensions=int(os.getenv("AZURE_OPENAI_EMB_MODEL_DIMENSIONS")),
                vector_search_profile_name="approximateProfile"
            ),
            SearchField(
                name="content",
                type=SearchFieldDataType.String,
                searchable=True,
                filterable=False,
                facetable=False,
                sortable=False
            ),
            SimpleField(
                name="metadata_storage_path",
                type=SearchFieldDataType.String,
                filterable=True
            ),
            SimpleField(
                name="metadata_storage_name",
                type=SearchFieldDataType.String,
                filterable=True
            )
        ],
        vector_search=VectorSearch(
            profiles=[
                VectorSearchProfile(
                    name="approximateProfile",
                    algorithm_configuration_name="approximateConfiguration",
                    vectorizer="text-embedding",
                    compression_configuration_name="scalarQuantization"
                )
            ],
            algorithms=[
                HnswAlgorithmConfiguration(name="approximateConfiguration")
            ],
            vectorizers=[
                AzureOpenAIVectorizer(
                    name="text-embedding",
                    azure_open_ai_parameters=AzureOpenAIParameters(
                        model_name=os.getenv("AZURE_OPENAI_EMB_MODEL_NAME"),
                        deployment_id=os.getenv("AZURE_OPENAI_EMB_DEPLOYMENT"),
                        resource_uri=os.getenv("AZURE_OPENAI_ENDPOINT"),
                        api_key=None
                    )
                )
            ],
            compressions=[
                ScalarQuantizationCompressionConfiguration(name="scalarQuantization")
            ]
        ),
        semantic_search=SemanticSearch(
            default_configuration_name="semantic-config",
            configurations=[
                SemanticConfiguration(
                    name="semantic-config",
                    prioritized_fields=SemanticPrioritizedFields(
                        title_field=SemanticField(field_name="metadata_storage_name"),
                        content_fields=[SemanticField(field_name="content")]
                    )
                )
            ]
        )
    )
    await search_index_client.create_or_update_index(index)

async def create_skillset(search_indexer_client: SearchIndexerClient):
    skillset = SearchIndexerSkillset(
        name=os.getenv("AZURE_SEARCH_SKILLSET"),
        skills=[
            AzureOpenAIEmbeddingSkill(
                description="Skill to generate embeddings via Azure OpenAI",  
                context="/document/pages/*",
                model_name=os.getenv("AZURE_OPENAI_EMB_MODEL_NAME"),
                resource_uri=os.getenv("AZURE_OPENAI_ENDPOINT"),  
                deployment_id=os.getenv("AZURE_OPENAI_EMB_DEPLOYMENT"),  
                api_key=None,  
                inputs=[  
                    InputFieldMappingEntry(name="text", source="/document/pages/*"),  
                ],  
                outputs=[  
                    OutputFieldMappingEntry(name="embedding")  
                ]
            ),
            SplitSkill(  
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
        ],
        index_projections=SearchIndexerIndexProjections(
            selectors=[
                SearchIndexerIndexProjectionSelector(
                    target_index_name=os.getenv("AZURE_SEARCH_INDEX"),
                    parent_key_field_name="document_id",
                    source_context="/document/pages/*",
                    mappings=[
                        InputFieldMappingEntry(
                            name="embedding",
                            source="/document/pages/*/embedding"
                        ),
                        InputFieldMappingEntry(
                            name="content",
                            source="/document/pages/*"
                        ),
                        InputFieldMappingEntry(
                            name="metadata_storage_path",
                            source="/document/metadata_storage_path"
                        ),
                        InputFieldMappingEntry(
                            name="metadata_storage_name",
                            source="/document/metadata_storage_name"
                        )
                    ]
                )
            ],
            parameters=SearchIndexerIndexProjectionsParameters(projection_mode=IndexProjectionMode.SKIP_INDEXING_PARENT_DOCUMENTS)
        )
    )
    await search_indexer_client.create_or_update_skillset(skillset)

async def create_datasource(search_indexer_client: SearchIndexerClient):
    datasource = SearchIndexerDataSourceConnection(
        name=os.getenv("AZURE_SEARCH_DATASOURCE"),
        type=SearchIndexerDataSourceType.AZURE_BLOB,
        connection_string=f"ResourceId={os.getenv('AZURE_STORAGE_ACCOUNT_ID')}",
        container=SearchIndexerDataContainer(name=os.getenv("AZURE_STORAGE_CONTAINER"))
    )
    await search_indexer_client.create_or_update_data_source_connection(datasource)

async def create_indexer(search_indexer_client: SearchIndexerClient):
    indexer = SearchIndexer(
        name=os.getenv("AZURE_SEARCH_INDEXER"),
        data_source_name=os.getenv("AZURE_SEARCH_DATASOURCE"),
        target_index_name=os.getenv("AZURE_SEARCH_INDEX"),
        skillset_name=os.getenv("AZURE_SEARCH_SKILLSET")
    )
    await search_indexer_client.create_or_update_indexer(indexer)

if __name__ == "__main__":
    asyncio.run(main())