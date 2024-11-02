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
        [ConfigurationKeyName("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")]
        public string AzureOpenAIEmbeddingDeployment { get; set; }

        /// <summary>
        /// Name of text embedding model in Azure OpenAI service
        /// </summary>
        [ConfigurationKeyName("AZURE_OPENAI_EMBEDDING_MODEL")]
        public string AzureOpenAIEmbeddingModel { get; set; }

        /// <summary>
        /// Dimensions for embedding model
        /// </summary>
        [ConfigurationKeyName("AZURE_OPENAI_EMBEDDING_DIMENSIONS")]
        public string AzureOpenAIEmbeddingDimensions { get; set; }

        /// <summary>
        /// Validate the configuration and set applicable defaults if necessary
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

            if (string.IsNullOrEmpty(AzureOpenAIEmbeddingDeployment))
            {
                AzureOpenAIEmbeddingDeployment = "text-embedding-3-small";
            }

            if (string.IsNullOrEmpty(AzureOpenAIEmbeddingModel))
            {
                AzureOpenAIEmbeddingModel = "text-embedding-3-small";
            }

            if (string.IsNullOrEmpty(AzureOpenAIEmbeddingDimensions))
            {
                AzureOpenAIEmbeddingDimensions = "1024";
            }
        }
    }
}