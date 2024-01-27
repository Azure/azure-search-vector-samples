using Microsoft.Extensions.Configuration;

namespace DotNetIntegratedVectorizationDemo
{
    /// <summary>
    /// Configuration for the demo app. Can be filled in from local.settings.json or environment variables
    /// </summary>
    public class Configuration
    {
        /// <summary>
        /// Service endpoint for the search service
        /// e.g. "https://your-search-service.search.windows.net
        /// </summary>
        [ConfigurationKeyName("AZURE_SEARCH_SERVICE_ENDPOINT")]
        public string ServiceEndpoint { get; set; }

        /// <summary>
        /// Index name in the search service
        /// e.g. sample-index
        /// </summary>
        [ConfigurationKeyName("AZURE_SEARCH_INDEX_NAME")]
        public string IndexName { get; set; }

        /// <summary>
        /// Admin API key for search service
        /// Optional, if not specified attempt to use DefaultAzureCredential
        /// </summary>
        [ConfigurationKeyName("AZURE_SEARCH_ADMIN_KEY")]
        public string AdminKey { get; set; }

        /// <summary>
        /// Azure Open AI key
        /// Optional, if not specified attempt to use DefaultAzureCredential
        /// </summary>
        [ConfigurationKeyName("AZURE_OPENAI_API_KEY")]
        public string AzureOpenAIApiKey { get; set; }

        /// <summary>
        /// Endpoint for Azure OpenAI service
        /// </summary>
        [ConfigurationKeyName("AZURE_OPENAI_ENDPOINT")]
        public string AzureOpenAIEndpoint { get; set; }

        /// <summary>
        /// Name of text embedding model deployment in Azure OpenAI service
        /// </summary>
        [ConfigurationKeyName("AZURE_OPENAI_EMBEDDING_DEPLOYED_MODEL")]
        public string AzureOpenAIEmbeddingDeployedModel { get; set; }

        /// <summary>
        /// Connection string for blob indexer datasource
        /// </summary>
        [ConfigurationKeyName("AZURE_BLOB_CONNECTION_STRING")]
        public string BlobConnectionString { get; set; }

        /// <summary>
        /// Container name for blob datasource
        /// </summary>
        [ConfigurationKeyName("AZURE_BLOB_CONTAINER_NAME")]
        public string BlobContainerName { get; set; }

        /// <summary>
        /// Validate the configuration
        /// </summary>
        /// <exception cref="ArgumentException">If any parameters are invalid</exception>
        public void Validate()
        {
            if (!Uri.TryCreate(ServiceEndpoint, UriKind.Absolute, out _))
            {
                throw new ArgumentException("Must specify service endpoint", nameof(ServiceEndpoint));
            }

            if (string.IsNullOrEmpty(IndexName))
            {
                throw new ArgumentException("Must specify index name", nameof(IndexName));
            }

            if (!Uri.TryCreate(AzureOpenAIEndpoint, UriKind.Absolute, out _))
            {
                throw new ArgumentException("Must specify Azure OpenAI endpoint", nameof(AzureOpenAIEndpoint));
            }

            if (string.IsNullOrEmpty(BlobConnectionString))
            {
                throw new ArgumentException("Must specify blob connection string", nameof(BlobConnectionString));
            }

            if (string.IsNullOrEmpty(BlobContainerName))
            {
                throw new ArgumentException("Must specify blob container name", nameof(BlobContainerName));
            }
        }
    }
}