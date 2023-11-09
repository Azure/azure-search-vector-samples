using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Azure;
using Azure.AI.OpenAI;
using Azure.Search.Documents;
using Azure.Search.Documents.Indexes;
using Azure.Search.Documents.Indexes.Models;
using Azure.Search.Documents.Models;
using Microsoft.Extensions.Configuration;

namespace DotNetIntegratedVectorizationDemo
{
    class Program
    {
        static async Task Main(string[] args)
        {
            var configuration = new ConfigurationBuilder()
                .SetBasePath(Directory.GetCurrentDirectory())
                .AddJsonFile("local.settings.json")
                .Build();

            // Load environment variables  
            var serviceEndpoint = configuration["AZURE_SEARCH_SERVICE_ENDPOINT"] ?? string.Empty;
            var indexName = configuration["AZURE_SEARCH_INDEX_NAME"] ?? string.Empty;
            var key = configuration["AZURE_SEARCH_ADMIN_KEY"] ?? string.Empty;
            var openaiApiKey = configuration["AZURE_OPENAI_API_KEY"] ?? string.Empty;
            var openaiEndpoint = configuration["AZURE_OPENAI_ENDPOINT"] ?? string.Empty;
            var blobConnectionString = configuration["AZURE_BLOB_CONNECTION_STRING"] ?? string.Empty;
            var blobContainerName = configuration["AZURE_BLOB_CONTAINER_NAME"] ?? string.Empty;

            // Initialize OpenAI client  
            var credential = new AzureKeyCredential(openaiApiKey);
            var openAIClient = new OpenAIClient(new Uri(openaiEndpoint), credential);

            // Initialize Azure AI Search clients  
            var searchCredential = new AzureKeyCredential(key);
            var indexClient = new SearchIndexClient(new Uri(serviceEndpoint), searchCredential);
            var indexerClient = new SearchIndexerClient(new Uri(serviceEndpoint), searchCredential);
            var searchClient = indexClient.GetSearchClient(indexName);

            // ASK USER "Would you like to index? (y/n)"  
            Console.Write("Would you like to index or query? (i/q): ");
            string choice = Console.ReadLine()?.ToLower() ?? string.Empty;

            if (choice == "i")
            {
                // Create an Index  
                Console.WriteLine("Creating/Updating the index...");
                var index = GetSampleIndex(indexName, openaiEndpoint, openaiApiKey);
                await indexClient.CreateOrUpdateIndexAsync(index).ConfigureAwait(false);
                Console.WriteLine("Index Created/Updated!");

                // Create a Data Source Connection  
                Console.WriteLine("Creating/Updating the data source connection...");
                var dataSource = new SearchIndexerDataSourceConnection(
                    $"{indexName}-blob",
                    SearchIndexerDataSourceType.AzureBlob,
                    connectionString: blobConnectionString,
                    container: new SearchIndexerDataContainer(blobContainerName));
                indexerClient.CreateOrUpdateDataSourceConnection(dataSource);
                Console.WriteLine("Data Source Created/Updated!");

                // Create a Skillset  
                Console.WriteLine("Creating/Updating the skillset...");
                var skillset = new SearchIndexerSkillset($"{indexName}-skillset", new List<SearchIndexerSkill>
                {  
                    // Add required skills here    
                    new SplitSkill(
                        new List<InputFieldMappingEntry>
                        {
                            new InputFieldMappingEntry("text") { Source = "/document/content" }
                        },
                        new List<OutputFieldMappingEntry>
                        {
                            new OutputFieldMappingEntry("textItems") { TargetName = "pages" }
                        })
                    {
                        Context = "/document",
                        TextSplitMode = TextSplitMode.Pages,
                        MaximumPageLength = 500,
                        PageOverlapLength = 100,
                    },
                    new AzureOpenAIEmbeddingSkill(
                        new List<InputFieldMappingEntry>
                        {
                            new InputFieldMappingEntry("text") { Source = "/document/pages/*" }
                        },
                        new List<OutputFieldMappingEntry>
                        {
                            new OutputFieldMappingEntry("embedding") { TargetName = "vector" }
                        }
                    )
                    {
                        Context = "/document/pages/*",
                        ResourceUri = new Uri(openaiEndpoint),
                        ApiKey = openaiApiKey,
                        DeploymentId = "text-embedding-ada-002",
                    }
                });
                await indexerClient.CreateOrUpdateSkillsetAsync(skillset).ConfigureAwait(false);
                Console.WriteLine("Skillset Created/Updated!");

                // Create an Indexer  
                Console.WriteLine("Creating/Updating the indexer...");
                var indexer = new SearchIndexer($"{indexName}-indexer", dataSource.Name, indexName)
                {
                    Description = "Indexer to chunk documents, generate embeddings, and add to the index",
                    Schedule = new IndexingSchedule(TimeSpan.FromDays(1))
                    {
                        StartTime = DateTimeOffset.Now
                    },
                    Parameters = new IndexingParameters()
                    {
                        BatchSize = 1,
                        MaxFailedItems = 0,
                        MaxFailedItemsPerBatch = 0,
                    },
                    SkillsetName = skillset.Name,
                };
                await indexerClient.CreateOrUpdateIndexerAsync(indexer).ConfigureAwait(false);
                Console.WriteLine("Indexer Created/Updated!");

                // Run Indexer  
                Console.WriteLine("Running the indexer...");
                await indexerClient.RunIndexerAsync(indexer.Name).ConfigureAwait(false);
                Console.WriteLine("Indexer is Running!");
            }
            else if (choice == "q")
            {
                Console.WriteLine("Choose a query approach:");
                Console.WriteLine("1. Single Vector Search");
                Console.WriteLine("2. Single Vector Search with Filter");
                Console.WriteLine("3. Simple Hybrid Search");
                Console.WriteLine("4. Semantic Hybrid Search");
                Console.Write("Enter the number of the desired approach: ");
                if (int.TryParse(Console.ReadLine(), out int queryChoice))
                {
                    Console.WriteLine("Type a Vector search query:");
                    string inputQuery = Console.ReadLine() ?? string.Empty;

                    switch (queryChoice)
                    {
                        case 1:
                            await SingleVectorSearch(searchClient, inputQuery);
                            break;
                        case 2:
                            Console.Write("Enter a filter for the search (e.g., category eq 'Databases'): ");
                            string filter = Console.ReadLine() ?? string.Empty;
                            await SingleVectorSearchWithFilter(searchClient, inputQuery, filter);
                            break;
                        case 3:
                            await SimpleHybridSearch(searchClient, inputQuery);
                            break;
                        case 4:
                            await SemanticHybridSearch(searchClient, inputQuery);
                            break;
                        default:
                            Console.WriteLine("Invalid choice. Exiting...");
                            break;
                    }
                }
                else
                {
                    Console.WriteLine("Invalid choice. Exiting...");
                }
            }
        }

        internal static SearchIndex GetSampleIndex(string name, string openaiEndpoint, string openaiApiKey)
        {
            string vectorSearchHnswProfile = "my-vector-profile";
            string vectorSearchExhasutiveKnnProfile = "myExhaustiveKnnProfile";
            string vectorSearchHnswConfig = "myHnsw";
            string vectorSearchExhaustiveKnnConfig = "myExhaustiveKnn";
            string vectorSearchVectorizer = "myOpenAIVectorizer";
            string semanticSearchConfig = "my-semantic-config";
            int modelDimensions = 1536;

            SearchIndex searchIndex = new(name)
            {
                VectorSearch = new()
                {
                    Profiles =
            {
                new VectorSearchProfile(vectorSearchHnswProfile, vectorSearchHnswConfig)
                {
                    Vectorizer = vectorSearchVectorizer
                },
                new VectorSearchProfile(vectorSearchExhasutiveKnnProfile, vectorSearchExhaustiveKnnConfig)
            },
                    Algorithms =
            {
                new HnswVectorSearchAlgorithmConfiguration(vectorSearchHnswConfig),
                new ExhaustiveKnnVectorSearchAlgorithmConfiguration(vectorSearchExhaustiveKnnConfig)
            },
                    Vectorizers =
            {
                new AzureOpenAIVectorizer(vectorSearchVectorizer)
                {
                    AzureOpenAIParameters = new AzureOpenAIParameters()
                    {
                        ResourceUri = new Uri(openaiEndpoint),
                        ApiKey = openaiApiKey,
                        DeploymentId = "text-embedding-ada-002",
                    }
                }
            }
                },
                SemanticSettings = new()
                {
                    Configurations =
            {
                new SemanticConfiguration(semanticSearchConfig, new()
                {
                    TitleField = new() { FieldName = "title" },
                    ContentFields =
                    {
                        new() { FieldName = "chunk" }
                    },
                })
            },
                },
                Fields =
        {
            new SearchableField("parent_id") { IsFilterable = true, IsSortable = true, IsFacetable = true },
            new SearchableField("chunk_id") { IsKey = true, IsFilterable = true, IsSortable = true, IsFacetable = true, AnalyzerName = LexicalAnalyzerName.Keyword },
            new SearchableField("title"),
            new SearchableField("chunk"),
            new SearchField("vector", SearchFieldDataType.Collection(SearchFieldDataType.Single))
            {
                IsSearchable = true,
                VectorSearchDimensions = modelDimensions,
                VectorSearchProfile = vectorSearchHnswProfile
            },
            new SearchableField("category") { IsFilterable = true, IsSortable = true, IsFacetable = true },
        },
            };

            return searchIndex;
        }

        internal static async Task SingleVectorSearch(SearchClient searchClient, string query, int k = 3)
        {
            // Perform the vector similarity search  
            var searchOptions = new SearchOptions
            {
                VectorQueries = { new VectorizableTextQuery()
        {
            Text = query,
            KNearestNeighborsCount = k,
            Fields = { "vector" }
        } },
                Size = k,
                Select = { "title", "chunk_id", "chunk", },
            };
            SearchResults<SearchDocument> response = await searchClient.SearchAsync<SearchDocument>(null, searchOptions);
            int count = 0;
            await foreach (SearchResult<SearchDocument> result in response.GetResultsAsync())
            {
                count++;
                Console.WriteLine($"Title: {result.Document["title"]}");
                Console.WriteLine($"Score: {result.Score}\n");
                Console.WriteLine($"Content: {result.Document["chunk"]}");
            }
            Console.WriteLine($"Total Results: {count}");
        }
        internal static async Task SingleVectorSearchWithFilter(SearchClient searchClient, string query, string filter, int k = 3)
        {
            // Perform the vector similarity search with filter  
            var searchOptions = new SearchOptions
            {
                VectorQueries = { new VectorizableTextQuery()
        {
            Text = query,
            KNearestNeighborsCount = k,
            Fields = { "vector" }
        } },
                Filter = filter,
                Size = k,
                Select = { "title", "chunk", "category" },
            };

            SearchResults<SearchDocument> response = await searchClient.SearchAsync<SearchDocument>(null, searchOptions);

            int count = 0;
            await foreach (SearchResult<SearchDocument> result in response.GetResultsAsync())
            {
                count++;
                Console.WriteLine($"Title: {result.Document["title"]}");
                Console.WriteLine($"Score: {result.Score}\n");
                Console.WriteLine($"Content: {result.Document["chunk"]}");
            }
            Console.WriteLine($"Total Results: {count}");
        }

        internal static async Task SimpleHybridSearch(SearchClient searchClient, string query, int k = 3)
        {
            // Perform the simple hybrid search  
            var searchOptions = new SearchOptions
            {
                VectorQueries = { new VectorizableTextQuery()
        {
            Text = query,
            KNearestNeighborsCount = k,
            Fields = { "vector" }
        } },
                Size = k,
                Select = { "title", "chunk", "category" },
            };

            SearchResults<SearchDocument> response = await searchClient.SearchAsync<SearchDocument>(query, searchOptions);

            int count = 0;
            await foreach (SearchResult<SearchDocument> result in response.GetResultsAsync())
            {
                count++;
                Console.WriteLine($"Title: {result.Document["title"]}");
                Console.WriteLine($"Score: {result.Score}\n");
                Console.WriteLine($"Content: {result.Document["chunk"]}");
            }
            Console.WriteLine($"Total Results: {count}");
        }

        internal static async Task SemanticHybridSearch(SearchClient searchClient, string query, int k = 3)
        {
            // Perform the semantic hybrid search  
            var searchOptions = new SearchOptions
            {
                VectorQueries = { new VectorizableTextQuery()
        {
            Text = query,
            KNearestNeighborsCount = k,
            Fields = { "vector" }
        } },
                QueryType = SearchQueryType.Semantic,
                QueryLanguage = QueryLanguage.EnUs,
                SemanticConfigurationName = "my-semantic-config",
                QueryCaption = QueryCaptionType.Extractive,
                QueryAnswer = QueryAnswerType.Extractive,
                Size = k,
                Select = { "title", "chunk", "category" },
            };

            SearchResults<SearchDocument> response = await searchClient.SearchAsync<SearchDocument>(query, searchOptions);

            int count = 0;
            Console.WriteLine("Semantic Hybrid Search Results:\n");

            Console.WriteLine("Query Answer:");
            foreach (AnswerResult result in response.Answers)
            {
                Console.WriteLine($"Answer Highlights: {result.Highlights}");
                Console.WriteLine($"Answer Text: {result.Text}\n");
            }

            await foreach (SearchResult<SearchDocument> result in response.GetResultsAsync())
            {
                count++;
                Console.WriteLine($"Title: {result.Document["title"]}");
                Console.WriteLine($"Reranker Score: {result.RerankerScore}");
                Console.WriteLine($"Score: {result.Score}");
                Console.WriteLine($"Content: {result.Document["chunk"]}");

                if (result.Captions != null)
                {
                    var caption = result.Captions.FirstOrDefault();
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
    }
}

