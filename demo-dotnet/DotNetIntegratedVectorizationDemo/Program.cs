using Azure;
using Azure.AI.OpenAI;
using Azure.Identity;
using Azure.Search.Documents;
using Azure.Search.Documents.Indexes;
using Azure.Search.Documents.Indexes.Models;
using Azure.Search.Documents.Models;
using Microsoft.Extensions.Configuration;

namespace DotNetIntegratedVectorizationDemo
{
    class Program
    {
        /// <summary>
        /// .NET Integrated Vectorization Demo
        /// </summary>
        /// <param name="setupAndRunIndexer">Sets up integrated vectorization indexer with a skillset.</param>
        /// <param name="query">Optional text of the search query. By default no query is run. Unless --textOnly is specified, this query is automatically vectorized.</param>
        /// <param name="filter">Optional filter of the search query. By default no filter is applied</param>
        /// <param name="k">How many results to return if running a query.</param>
        /// <param name="exhaustive">Optional, specifies if the query skips using the index and computes the true nearest neighbors. Can only be used with vector or hybrid queries.</param>
        /// <param name="textOnly">Optional, specifies if the query is vectorized before searching. If true, only the text indexed is used for search.</param>
        /// <param name="hybrid">Optional, specifies if the query combines text and vector results.</param>
        /// <param name="semantic">Optional, specifies if the semantic reranker is used to rerank results from the query.</param>
        static async Task Main(bool setupAndRunIndexer, string query = null, string filter = null, int k = 3, bool exhaustive = false, bool textOnly = false,  bool hybrid = false, bool semantic = false)
        {
            var configuration = new Configuration();
            new ConfigurationBuilder()
                .SetBasePath(Directory.GetCurrentDirectory())
                .AddEnvironmentVariables()
                .AddJsonFile("local.settings.json")
                .Build()
                .Bind(configuration);

            if (textOnly && hybrid)
            {
                throw new ArgumentException("Cannot specify textOnly with hybrid", nameof(textOnly));
            }

            if (exhaustive && textOnly)
            {
                throw new ArgumentException("Cannot specify exhaustive with textOnly", nameof(exhaustive));
            }

            configuration.Validate();
            var defaultCredential = new DefaultAzureCredential();
            var openAIClient = InitializeOpenAIClient(configuration, defaultCredential);
            var indexClient = InitializeSearchIndexClient(configuration, defaultCredential);
            var indexerClient = InitializeSearchIndexerClient(configuration, defaultCredential);
            var searchClient = indexClient.GetSearchClient(configuration.IndexName);

            if (setupAndRunIndexer)
            {
                await SetupAndRunIndexer(configuration, indexClient, indexerClient, openAIClient);
            }

            if (!string.IsNullOrEmpty(query))
            {
                await Search(searchClient, query, k, filter, exhaustive, textOnly, hybrid, semantic);
            }
        }

        internal static async Task SetupAndRunIndexer(Configuration configuration, SearchIndexClient indexClient, SearchIndexerClient indexerClient, OpenAIClient openAIClient)
        {
            // Create an Index  
            Console.WriteLine("Creating/Updating the index...");
            var index = GetSampleIndex(configuration);
            await indexClient.CreateOrUpdateIndexAsync(index);
            Console.WriteLine("Index Created/Updated!");

            // Create a Data Source Connection  
            Console.WriteLine("Creating/Updating the data source connection...");
            var dataSource = new SearchIndexerDataSourceConnection(
                $"{configuration.IndexName}-blob",
                SearchIndexerDataSourceType.AzureBlob,
                connectionString: configuration.BlobConnectionString,
                container: new SearchIndexerDataContainer(configuration.BlobContainerName));
            indexerClient.CreateOrUpdateDataSourceConnection(dataSource);
            Console.WriteLine("Data Source Created/Updated!");

            // Create a Skillset  
            Console.WriteLine("Creating/Updating the skillset...");
            var skillset = new SearchIndexerSkillset($"{configuration.IndexName}-skillset", new List<SearchIndexerSkill>
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
                    MaximumPageLength = 2000,
                    PageOverlapLength = 500,
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
                    ResourceUri = new Uri(configuration.AzureOpenAIEndpoint),
                    ApiKey = configuration.AzureOpenAIApiKey,
                    DeploymentId = configuration.AzureOpenAIEmbeddingDeployedModel,
                }
            })
            {
                IndexProjections = new SearchIndexerIndexProjections(new[]
                {
                    new SearchIndexerIndexProjectionSelector(configuration.IndexName, parentKeyFieldName: "parent_id", sourceContext: "/document/pages/*", mappings: new[]
                    {
                        new InputFieldMappingEntry("chunk")
                        {
                            Source = "/document/pages/*" 
                        },
                        new InputFieldMappingEntry("vector")
                        {
                            Source = "/document/pages/*/vector"
                        },
                        new InputFieldMappingEntry("title")
                        {
                            Source = "/document/metadata_storage_name"
                        }
                    })
                })
                {
                    Parameters = new SearchIndexerIndexProjectionsParameters
                    {
                        ProjectionMode = IndexProjectionMode.SkipIndexingParentDocuments
                    }
                }
            };
            await indexerClient.CreateOrUpdateSkillsetAsync(skillset).ConfigureAwait(false);
            Console.WriteLine("Skillset Created/Updated!");

            // Create an Indexer  
            Console.WriteLine("Creating/Updating the indexer...");
            var indexer = new SearchIndexer($"{configuration.IndexName}-indexer", dataSource.Name, configuration.IndexName)
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

        internal static OpenAIClient InitializeOpenAIClient(Configuration configuration, DefaultAzureCredential defaultCredential)
        {
            if (!string.IsNullOrEmpty(configuration.AzureOpenAIApiKey))
            {
                return new OpenAIClient(new Uri(configuration.AzureOpenAIEndpoint), new AzureKeyCredential(configuration.AzureOpenAIApiKey));
            }

            return new OpenAIClient(new Uri(configuration.AzureOpenAIEndpoint), defaultCredential);
        }

        internal static SearchIndexClient InitializeSearchIndexClient(Configuration configuration, DefaultAzureCredential defaultCredential)
        {
            if (!string.IsNullOrEmpty(configuration.AdminKey))
            {
                return new SearchIndexClient(new Uri(configuration.ServiceEndpoint), new AzureKeyCredential(configuration.AdminKey));
            }

            return new SearchIndexClient(new Uri(configuration.ServiceEndpoint), defaultCredential);
        }

        internal static SearchIndexerClient InitializeSearchIndexerClient(Configuration configuration, DefaultAzureCredential defaultCredential)
        {
            if (!string.IsNullOrEmpty(configuration.AdminKey))
            {
                return new SearchIndexerClient(new Uri(configuration.ServiceEndpoint), new AzureKeyCredential(configuration.AdminKey));
            }

            return new SearchIndexerClient(new Uri(configuration.ServiceEndpoint), defaultCredential);
        }

        internal static SearchIndex GetSampleIndex(Configuration configuration)
        {
            const string vectorSearchHnswProfile = "my-vector-profile";
            const string vectorSearchExhasutiveKnnProfile = "myExhaustiveKnnProfile";
            const string vectorSearchHnswConfig = "myHnsw";
            const string vectorSearchExhaustiveKnnConfig = "myExhaustiveKnn";
            const string vectorSearchVectorizer = "myOpenAIVectorizer";
            const string semanticSearchConfig = "my-semantic-config";
            const int modelDimensions = 1536;

            SearchIndex searchIndex = new(configuration.IndexName)
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
                        new HnswAlgorithmConfiguration(vectorSearchHnswConfig),
                        new ExhaustiveKnnAlgorithmConfiguration(vectorSearchExhaustiveKnnConfig)
                    },
                    Vectorizers =
                    {
                        new AzureOpenAIVectorizer(vectorSearchVectorizer)
                        {
                            AzureOpenAIParameters = new AzureOpenAIParameters()
                            {
                                ResourceUri = new Uri(configuration.AzureOpenAIEndpoint),
                                ApiKey = configuration.AzureOpenAIApiKey,
                                DeploymentId = configuration.AzureOpenAIEmbeddingDeployedModel,
                            }
                        }
                    }
                },
                SemanticSearch = new()
                {
                    Configurations =
                    {
                        new SemanticConfiguration(semanticSearchConfig, new()
                        {
                            TitleField = new SemanticField(fieldName: "title"),
                            ContentFields =
                            {
                                new SemanticField(fieldName: "chunk")
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
                        VectorSearchProfileName = vectorSearchHnswProfile
                    },
                    new SearchableField("category") { IsFilterable = true, IsSortable = true, IsFacetable = true },
                },
            };

            return searchIndex;
        }

        internal static async Task Search(SearchClient searchClient, string query, int k = 3, string filter = null, bool textOnly = false, bool exhaustive = false, bool hybrid = false, bool semantic = false)
        {
            // Perform the vector similarity search  
            var searchOptions = new SearchOptions
            {
                Filter = filter,
                Size = k,
                Select = { "title", "chunk_id", "chunk", },
                IncludeTotalCount = true
            };
            if (!textOnly)
            {
                searchOptions.VectorSearch = new() {
                    Queries = {
                        new VectorizableTextQuery(text: query)
                        {
                            KNearestNeighborsCount = k,
                            Fields = { "vector" },
                            Exhaustive = exhaustive
                        }
                    },
                    
                };
            }
            if (semantic)
            {
                searchOptions.QueryType = SearchQueryType.Semantic;
                searchOptions.SemanticSearch = new SemanticSearchOptions
                {
                    SemanticConfigurationName = "my-semantic-config",
                    QueryCaption = new QueryCaption(QueryCaptionType.Extractive),
                    QueryAnswer = new QueryAnswer(QueryAnswerType.Extractive)
                };
            }
            string queryText = (textOnly || hybrid || semantic) ? query : null;
            SearchResults<SearchDocument> response = await searchClient.SearchAsync<SearchDocument>(queryText, searchOptions);

            if (response.SemanticSearch?.Answers?.Count > 0)
            {
                Console.WriteLine("Query Answers:");
                foreach (QueryAnswerResult answer in response.SemanticSearch.Answers)
                {
                    Console.WriteLine($"Answer Highlights: {answer.Highlights}");
                    Console.WriteLine($"Answer Text: {answer.Text}");
                }
            }

            await foreach (SearchResult<SearchDocument> result in response.GetResultsAsync())
            {
                Console.WriteLine($"Title: {result.Document["title"]}");
                Console.WriteLine($"Score: {result.Score}\n");
                Console.WriteLine($"Content: {result.Document["chunk"]}");
                if (result.SemanticSearch?.Captions?.Count > 0)
                {
                    QueryCaptionResult firstCaption = result.SemanticSearch.Captions[0];
                    Console.WriteLine($"First Caption Highlights: {firstCaption.Highlights}");
                    Console.WriteLine($"First Caption Text: {firstCaption.Text}");
                }
            }
            Console.WriteLine($"Total Results: {response.TotalCount}");
        }
    }
}
