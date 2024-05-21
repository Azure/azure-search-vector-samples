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
    IndexingParameters,
    IndexingParametersConfiguration,
    BlobIndexerImageAction,
    VisionVectorizeSkill,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    SearchFieldDataType,
    ScalarQuantizationCompressionConfiguration,
    VectorSearchProfile,
    VectorSearch,
    SearchField,
    SearchableField,
    SimpleField,
    AIServicesVisionVectorizer,
    AIServicesVisionParameters,
    HnswAlgorithmConfiguration,
    LexicalAnalyzerName
)
import os
import glob
import datetime

current_file_directory = os.path.dirname(os.path.abspath(__file__))
samples_path = os.path.join(current_file_directory, "..", "..", "..", "..", "data", "images", "apples")
vision_model_version = "2023-04-15"

async def main():
    async with DefaultAzureCredential() as credential:
        print("Uploading sample images...")
        blob_url = os.getenv("AZURE_STORAGE_ACCOUNT_BLOB_URL")
        async with BlobServiceClient(account_url=blob_url, credential=credential) as blob_service_client:
            await upload_images(blob_service_client)

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

async def upload_images(blob_service_client: BlobServiceClient):
    container_client = blob_service_client.get_container_client(os.getenv("AZURE_STORAGE_CONTAINER"))
    image_paths = glob.glob(os.path.join(samples_path, "*.jpeg"))
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
                vector_search_dimensions=1024,
                vector_search_profile_name="approximateProfile"
            ),
            SimpleField(
                name="metadata_storage_path",
                type=SearchFieldDataType.String,
                filterable=True
            )
        ],
        vector_search=VectorSearch(
            profiles=[
                VectorSearchProfile(
                    name="approximateProfile",
                    algorithm_configuration_name="approximateConfiguration",
                    vectorizer="multimodal",
                    compression_configuration_name="scalarQuantization"
                )
            ],
            algorithms=[
                HnswAlgorithmConfiguration(name="approximateConfiguration")
            ],
            vectorizers=[
                AIServicesVisionVectorizer(
                    name="multimodal",
                    ai_services_vision_parameters=AIServicesVisionParameters(
                        model_version=vision_model_version,
                        resource_uri=os.getenv("AZURE_AI_SERVICES_ENDPOINT"),
                        api_key=None
                    )
                )
            ],
            compressions=[
                ScalarQuantizationCompressionConfiguration(name="scalarQuantization")
            ]
        )
    )
    await search_index_client.create_or_update_index(index)

async def create_skillset(search_indexer_client: SearchIndexerClient):
    skillset = SearchIndexerSkillset(
        name=os.getenv("AZURE_SEARCH_SKILLSET"),
        skills=[
            VisionVectorizeSkill(
                name="visionvectorizer",
                context="/document/normalized_images/*",
                inputs=[
                    InputFieldMappingEntry(
                        name="image",
                        source="/document/normalized_images/*"
                    )
                ],
                outputs=[
                    OutputFieldMappingEntry(
                        name="vector"
                    )
                ],
                model_version=vision_model_version
            )
        ],
        index_projections=SearchIndexerIndexProjections(
            selectors=[
                SearchIndexerIndexProjectionSelector(
                    target_index_name=os.getenv("AZURE_SEARCH_INDEX"),
                    parent_key_field_name="document_id",
                    source_context="/document/normalized_images/*",
                    mappings=[
                        InputFieldMappingEntry(
                            name="embedding",
                            source="/document/normalized_images/*/vector"
                        ),
                        InputFieldMappingEntry(
                            name="metadata_storage_path",
                            source="/document/metadata_storage_path"
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
        skillset_name=os.getenv("AZURE_SEARCH_SKILLSET"),
        parameters=IndexingParameters(
            configuration=IndexingParametersConfiguration(
                image_action=BlobIndexerImageAction.GENERATE_NORMALIZED_IMAGES,
                query_timeout=None
            )
        )
    )
    await search_indexer_client.create_or_update_indexer(indexer)

if __name__ == "__main__":
    asyncio.run(main())