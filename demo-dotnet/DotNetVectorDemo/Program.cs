using System.Text.Json;
using Azure;
using Azure.AI.OpenAI;
using Azure.Search.Documents;
using Azure.Search.Documents.Indexes;
using Azure.Search.Documents.Indexes.Models;
using Azure.Search.Documents.Models;
using Microsoft.Extensions.Configuration;

namespace DotNetVectorDemo
{
    class Program
    {
        private const string ModelName = "text-embedding-ada-002";
        private const int ModelDimensions = 1536;
        private const string SemanticSearchConfigName = "my-semantic-config";

        static async Task Main(string[] args)
        {
            var configuration = new ConfigurationBuilder().SetBasePath(Directory.GetCurrentDirectory()).AddJsonFile("local.settings.json").Build();

            // Load environment variables  
            var serviceEndpoint = configuration["AZURE_SEARCH_SERVICE_ENDPOINT"] ?? string.Empty;
            var indexName = configuration["AZURE_SEARCH_INDEX_NAME"] ?? string.Empty;
            var key = configuration["AZURE_SEARCH_ADMIN_KEY"] ?? string.Empty;
            var openaiApiKey = configuration["AZURE_OPENAI_API_KEY"] ?? string.Empty;
            var openaiEndpoint = configuration["AZURE_OPENAI_ENDPOINT"] ?? string.Empty;

            // Initialize OpenAI client  
            var credential = new AzureKeyCredential(openaiApiKey);
            var openAIClient = new OpenAIClient(new Uri(openaiEndpoint), credential);

            // Initialize Azure AI Search clients  
            var searchCredential = new AzureKeyCredential(key);
            var indexClient = new SearchIndexClient(new Uri(serviceEndpoint), searchCredential);
            var searchClient = indexClient.GetSearchClient(indexName);

            Console.Write("Would you like to index (y/n)? ");
            string indexChoice = Console.ReadLine()?.ToLower() ?? string.Empty;

            if (indexChoice == "y")
            {
                // Create the search index  
                indexClient.CreateOrUpdateIndex(GetSampleIndex(indexName));

                // Read input documents and generate embeddings  
                var inputJson = File.ReadAllText("../data/text-sample.json");
                var inputDocuments = JsonSerializer.Deserialize<List<Dictionary<string, object>>>(inputJson) ?? new List<Dictionary<string, object>>();

                var sampleDocuments = await GetSampleDocumentsAsync(openAIClient, inputDocuments);
                await searchClient.IndexDocumentsAsync(IndexDocumentsBatch.Upload(sampleDocuments));
            }

            Console.WriteLine("Choose a query approach:");
            Console.WriteLine("1. Single Vector Search");
            Console.WriteLine("2. Single Vector Search with Filter");
            Console.WriteLine("3. Simple Hybrid Search");
            Console.WriteLine("4. Semantic Hybrid Search");
            Console.Write("Enter the number of the desired approach: ");
            int choice = int.Parse(Console.ReadLine() ?? "0");

            Console.WriteLine("Type a Vector search query:");
            string inputQuery = Console.ReadLine() ?? string.Empty;

            switch (choice)
            {
                case 1:
                    await SingleVectorSearch(searchClient, openAIClient, inputQuery);
                    break;
                case 2:
                    Console.Write("Enter a filter for the search (e.g., category eq 'Databases'): ");
                    string filter = Console.ReadLine() ?? string.Empty;
                    await SingleVectorSearchWithFilter(searchClient, openAIClient, inputQuery, filter);
                    break;
                case 3:
                    await SimpleHybridSearch(searchClient, openAIClient, inputQuery);
                    break;
                case 4:
                    await SemanticHybridSearch(searchClient, openAIClient, inputQuery);
                    break;
                default:
                    Console.WriteLine("Invalid choice. Exiting...");
                    break;
            }
        }

        // Function to generate embeddings  
        private static async Task<IReadOnlyList<float>> GenerateEmbeddings(string text, OpenAIClient openAIClient)
        {
            var response = await openAIClient.GetEmbeddingsAsync(ModelName, new EmbeddingsOptions(text));
            return response.Value.Data[0].Embedding;
        }

        internal static async Task SingleVectorSearch(SearchClient searchClient, OpenAIClient openAIClient, string query, int k = 3)
        {
            // Generate the embedding for the query  
            var queryEmbeddings = await GenerateEmbeddings(query, openAIClient);

            // Perform the vector similarity search  
            var searchOptions = new SearchOptions
            {
                VectorSearch = new()
                {
                    Queries = { new VectorizedQuery(queryEmbeddings.ToArray()) { KNearestNeighborsCount = 3, Fields = { "contentVector" } } }
                },
                Size = k,
                Select = { "title", "content", "category" },
            };

            SearchResults<SearchDocument> response = await searchClient.SearchAsync<SearchDocument>(null, searchOptions);

            int count = 0;
            await foreach (SearchResult<SearchDocument> result in response.GetResultsAsync())
            {
                count++;
                Console.WriteLine($"Title: {result.Document["title"]}");
                Console.WriteLine($"Score: {result.Score}\n");
                Console.WriteLine($"Content: {result.Document["content"]}");
                Console.WriteLine($"Category: {result.Document["category"]}\n");
            }
            Console.WriteLine($"Total Results: {count}");
        }

        internal static async Task SingleVectorSearchWithFilter(SearchClient searchClient, OpenAIClient openAIClient, string query, string filter, int k = 3)
        {
            // Generate the embedding for the query  
            var queryEmbeddings = await GenerateEmbeddings(query, openAIClient);

            // Perform the vector similarity search  
            var searchOptions = new SearchOptions
            {
                VectorSearch = new()
                {
                    Queries = { new VectorizedQuery(queryEmbeddings.ToArray()) { KNearestNeighborsCount = k, Fields = { "contentVector" } } }
                },
                Filter = filter,
                Select = { "title", "content", "category" },
            };

            SearchResults<SearchDocument> response = await searchClient.SearchAsync<SearchDocument>(null, searchOptions);

            int count = 0;
            await foreach (SearchResult<SearchDocument> result in response.GetResultsAsync())
            {
                count++;
                Console.WriteLine($"Title: {result.Document["title"]}");
                Console.WriteLine($"Score: {result.Score}\n");
                Console.WriteLine($"Content: {result.Document["content"]}");
                Console.WriteLine($"Category: {result.Document["category"]}\n");
            }
            Console.WriteLine($"Total Results: {count}");
        }

        internal static async Task SimpleHybridSearch(SearchClient searchClient, OpenAIClient openAIClient, string query, int k = 3)
        {
            // Generate the embedding for the query  
            var queryEmbeddings = await GenerateEmbeddings(query, openAIClient);

            // Perform the vector similarity search  
            var searchOptions = new SearchOptions
            {
                VectorSearch = new()
                {
                    Queries = { new VectorizedQuery(queryEmbeddings.ToArray()) { KNearestNeighborsCount = k, Fields = { "contentVector" } } }
                },
                Size = k,
                Select = { "title", "content", "category" },
            };

            SearchResults<SearchDocument> response = await searchClient.SearchAsync<SearchDocument>(query, searchOptions);

            int count = 0;
            await foreach (SearchResult<SearchDocument> result in response.GetResultsAsync())
            {
                count++;
                Console.WriteLine($"Title: {result.Document["title"]}");
                Console.WriteLine($"Score: {result.Score}\n");
                Console.WriteLine($"Content: {result.Document["content"]}");
                Console.WriteLine($"Category: {result.Document["category"]}\n");
            }
            Console.WriteLine($"Total Results: {count}");
        }

        internal static async Task SemanticHybridSearch(SearchClient searchClient, OpenAIClient openAIClient, string query, int k = 3)
        {
            try
            {
                // Generate the embedding for the query  
                var queryEmbeddings = await GenerateEmbeddings(query, openAIClient);

                // Perform the vector similarity search  
                var searchOptions = new SearchOptions
                {
                    VectorSearch = new()
                    {
                        Queries = { new VectorizedQuery(queryEmbeddings.ToArray()) { KNearestNeighborsCount = 3, Fields = { "contentVector" } } }
                    },
                    SemanticSearch = new()
                    {
                        SemanticConfigurationName = "my-semantic-config",
                        QueryCaption = new(QueryCaptionType.Extractive),
                        QueryAnswer = new(QueryAnswerType.Extractive),
                    },
                    QueryType = SearchQueryType.Semantic,
                    Size = k,
                    Select = { "title", "content", "category" },

                };

                SearchResults<SearchDocument> response = await searchClient.SearchAsync<SearchDocument>(query, searchOptions);

                int count = 0;
                Console.WriteLine($"Semantic Hybrid Search Results:");

                Console.WriteLine($"\nQuery Answer:");
                foreach (QueryAnswerResult result in response.SemanticSearch.Answers)
                {
                    Console.WriteLine($"Answer Highlights: {result.Highlights}");
                    Console.WriteLine($"Answer Text: {result.Text}");
                }

                await foreach (SearchResult<SearchDocument> result in response.GetResultsAsync())
                {
                    count++;
                    Console.WriteLine($"Title: {result.Document["title"]}");
                    Console.WriteLine($"Reranker Score: {result.SemanticSearch.RerankerScore}");
                    Console.WriteLine($"Score: {result.Score}");
                    Console.WriteLine($"Content: {result.Document["content"]}");
                    Console.WriteLine($"Category: {result.Document["category"]}\n");

                    if (result.SemanticSearch.Captions != null)
                    {
                        var caption = result.SemanticSearch.Captions.FirstOrDefault();
                        if (caption != null)
                        {
                            if (!string.IsNullOrEmpty(caption.Highlights))
                            {
                                Console.WriteLine($"Caption Highlights: {caption.Highlights}\n");
                            }
                            else
                            {
                                Console.WriteLine($"Caption Text: {caption.Text}\n");
                            }
                        }
                    }
                }
                Console.WriteLine($"Total Results: {count}");
            }
            catch (NullReferenceException)
            {
                Console.WriteLine("Total Results: 0");
            }
        }

        internal static SearchIndex GetSampleIndex(string name)
        {
            string vectorSearchProfile = "my-vector-profile";
            string vectorSearchHnswConfig = "my-hnsw-vector-config";

            SearchIndex searchIndex = new(name)
            {
                VectorSearch = new()
                {
                    Profiles =
                {
                    new VectorSearchProfile(vectorSearchProfile, vectorSearchHnswConfig)
                },
                    Algorithms =
                {
                    new HnswAlgorithmConfiguration(vectorSearchHnswConfig)
                }
                },
                SemanticSearch = new()
                {

                    Configurations =
                    {
                       new SemanticConfiguration(SemanticSearchConfigName, new()
                       {
                           TitleField = new SemanticField("title"),
                           ContentFields =
                           {
                            new SemanticField("content")
                           },
                KeywordsFields =
                {
                    new SemanticField("category")
                }

                       })

                },
                },
                Fields =
            {
                new SimpleField("id", SearchFieldDataType.String) { IsKey = true, IsFilterable = true, IsSortable = true, IsFacetable = true },
                new SearchableField("title") { IsFilterable = true, IsSortable = true },
                new SearchableField("content") { IsFilterable = true },
                new SearchField("titleVector", SearchFieldDataType.Collection(SearchFieldDataType.Single))
                {
                    IsSearchable = true,
                    VectorSearchDimensions = ModelDimensions,
                    VectorSearchProfileName = vectorSearchProfile
                },
                new SearchField("contentVector", SearchFieldDataType.Collection(SearchFieldDataType.Single))
                {
                    IsSearchable = true,
                    VectorSearchDimensions = ModelDimensions,
                    VectorSearchProfileName = vectorSearchProfile
                },
                new SearchableField("category") { IsFilterable = true, IsSortable = true, IsFacetable = true }
            }
            };

            return searchIndex;
        }

        internal static async Task<List<SearchDocument>> GetSampleDocumentsAsync(OpenAIClient openAIClient, List<Dictionary<string, object>> inputDocuments)
        {
            List<SearchDocument> sampleDocuments = new List<SearchDocument>();

            foreach (var document in inputDocuments)
            {
                string title = document["title"]?.ToString() ?? string.Empty;
                string content = document["content"]?.ToString() ?? string.Empty;

                float[] titleEmbeddings = (await GenerateEmbeddings(title, openAIClient)).ToArray();
                float[] contentEmbeddings = (await GenerateEmbeddings(content, openAIClient)).ToArray();

                document["titleVector"] = titleEmbeddings;
                document["contentVector"] = contentEmbeddings;
                sampleDocuments.Add(new SearchDocument(document));
            }

            return sampleDocuments;
        }
    }
}
