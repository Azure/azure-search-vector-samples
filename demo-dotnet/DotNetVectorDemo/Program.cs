using System;
using System.CommandLine;
using System.Text.Json;
using Azure;
using Azure.AI.OpenAI;
using Azure.Identity;
using Azure.Search.Documents;
using Azure.Search.Documents.Indexes;
using Azure.Search.Documents.Indexes.Models;
using Azure.Search.Documents.Models;
using DotNetIntegratedVectorizationDemo;
using Microsoft.Extensions.Configuration;
using OpenAI;
using OpenAI.Embeddings;
using System.Reflection;

namespace DotNetVectorDemo
{
    class Program
    {
        public const string SampleVectorDocumentsPath = "vector-sample.json";

        /// <summary>
        /// .NET Vector demo
        /// </summary>
        /// <param name="setupIndex">Indexes sample documents. text-embedding-3-small embeddings with a dimension of 1024 are used</param>
        /// <param name="query">Optional text of the search query. By default no query is run. Unless --textOnly is specified, this query is automatically vectorized.</param>
        /// <param name="filter">Optional filter of the search query. By default no filter is applied</param>
        /// <param name="k">How many nearest neighbors to use for vector search. Defaults to 50</param>
        /// <param name="top">How nany results to return. Defaults to 3</param>
        /// <param name="exhaustive">Optional, specifies if the query skips using the index and computes the true nearest neighbors. Can only be used with vector or hybrid queries.</param>
        /// <param name="textOnly">Optional, specifies if the query is vectorized before searching. If true, only the text indexed is used for search.</param>
        /// <param name="hybrid">Optional, specifies if the query combines text and vector results.</param>
        /// <param name="semantic">Optional, specifies if the semantic reranker is used to rerank results from the query.</param>
        /// <param name="debug">Optional, specifies if debug output is included from the query. Only valid values are disabled (default), semantic, or vector</param>
        static async Task Main(bool setupIndex, string query = null, string filter = null, int k = 50, int top = 3, bool exhaustive = false, bool textOnly = false, bool hybrid = false, bool semantic = false, string debug = "disabled")
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

            if (debug != "disabled" && debug != "semantic" && debug != "vector")
            {
                throw new ArgumentException("Debug must be disabled (default), semantic, or vector");
            }

            configuration.Validate();
            var defaultCredential = new DefaultAzureCredential();
            var azureOpenAIClient = InitializeOpenAIClient(configuration, defaultCredential);
            var indexClient = InitializeSearchIndexClient(configuration, defaultCredential);
            var searchClient = indexClient.GetSearchClient(configuration.IndexName);

            if (setupIndex)
            {
                await SetupIndexAsync(configuration, indexClient);
                await UploadSampleDocumentsAsync(configuration, searchClient, SampleVectorDocumentsPath);
            }

            if (!string.IsNullOrEmpty(query))
            {
                await Search(searchClient, query, k, top, filter, exhaustive, textOnly, hybrid, semantic, debug);
            }
        }

        internal static AzureOpenAIClient InitializeOpenAIClient(Configuration configuration, DefaultAzureCredential defaultCredential)
        {
            if (!string.IsNullOrEmpty(configuration.AzureOpenAIApiKey))
            {
                return new AzureOpenAIClient(new Uri(configuration.AzureOpenAIEndpoint), new AzureKeyCredential(configuration.AzureOpenAIApiKey));
            }

            return new AzureOpenAIClient(new Uri(configuration.AzureOpenAIEndpoint), defaultCredential);
        }

        internal static SearchIndexClient InitializeSearchIndexClient(Configuration configuration, DefaultAzureCredential defaultCredential)
        {
            if (!string.IsNullOrEmpty(configuration.AdminKey))
            {
                return new SearchIndexClient(new Uri(configuration.ServiceEndpoint), new AzureKeyCredential(configuration.AdminKey));
            }

            return new SearchIndexClient(new Uri(configuration.ServiceEndpoint), defaultCredential);
        }

        internal static async Task Search(SearchClient searchClient, string query, int k = 50, int top = 3, string filter = null, bool textOnly = false, bool exhaustive = false, bool hybrid = false, bool semantic = false, string debug = "disabled")
        {
            // Perform the vector similarity search  
            var searchOptions = new SearchOptions
            {
                Filter = filter,
                Size = top,
                Select = { "title", "id", "content", },
                IncludeTotalCount = true
            };
            if (!textOnly)
            {
                searchOptions.VectorSearch = new()
                {
                    Queries = {
                        new VectorizableTextQuery(text: query)
                        {
                            KNearestNeighborsCount = k,
                            Fields = { "titleVector" },
                            Exhaustive = exhaustive
                        },
                        new VectorizableTextQuery(text: query)
                        {
                            KNearestNeighborsCount = k,
                            Fields = { "contentVector" },
                            Exhaustive = exhaustive
                        },
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
                    QueryAnswer = new QueryAnswer(QueryAnswerType.Extractive),
                };
            }
            if (!string.IsNullOrEmpty(debug) && debug != "disabled")
            {
                if (!semantic)
                {
                    searchOptions.SemanticSearch = new SemanticSearchOptions();
                }
                searchOptions.SemanticSearch.Debug = new QueryDebugMode(debug);
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
                Console.WriteLine($"Content: {result.Document["content"]}");
                if (result.SemanticSearch?.Captions?.Count > 0)
                {
                    QueryCaptionResult firstCaption = result.SemanticSearch.Captions[0];
                    Console.WriteLine($"First Caption Highlights: {firstCaption.Highlights}");
                    Console.WriteLine($"First Caption Text: {firstCaption.Text}");
                }
                DocumentDebugInfo debugInfo = result.DocumentDebugInfo?.FirstOrDefault();
                if (debugInfo != null)
                {
                    if (debugInfo.Semantic != null)
                    {
                        var getFieldMessage = (QueryResultDocumentSemanticField field) => $"Field {field.Name}, State {field.State}";

                        if (debugInfo.Semantic.TitleField != null)
                        {
                            Console.WriteLine($"Title {getFieldMessage(debugInfo.Semantic.TitleField)}");
                        }

                        if (debugInfo.Semantic.ContentFields != null)
                        {
                            foreach (var contentField in debugInfo.Semantic.ContentFields)
                            {
                                Console.WriteLine($"Content {getFieldMessage(contentField)}");
                            }
                        }


                        if (debugInfo.Semantic.KeywordFields != null)
                        {
                            foreach (var keywordField in debugInfo.Semantic.KeywordFields)
                            {
                                Console.WriteLine($"Keyword {getFieldMessage(keywordField)}");
                            }
                        }
                    }

                    if (debugInfo.Vectors?.Subscores != null)
                    {
                        if (debugInfo.Vectors.Subscores.DocumentBoost != null)
                        {
                            Console.WriteLine($"Document Boost: {debugInfo.Vectors.Subscores.DocumentBoost}");
                        }

                        if (debugInfo.Vectors.Subscores.Text != null)
                        {
                            Console.WriteLine($"Document Text Score: {debugInfo.Vectors.Subscores.Text.SearchScore}");
                        }

                        int index = 1;
                        foreach (IDictionary<string, SingleVectorFieldResult> querySubscore in debugInfo.Vectors.Subscores.Vectors)
                        {
                            Console.WriteLine($"Vector Query {index} Debug Info:");
                            foreach (KeyValuePair<string, SingleVectorFieldResult> fieldSubscore in querySubscore) {
                                Console.WriteLine($"Vector Field: {fieldSubscore.Key}");
                                Console.WriteLine($"Vector Field @search.score: {fieldSubscore.Value.SearchScore}");
                                Console.WriteLine($"Vector Field similarity: {fieldSubscore.Value.VectorSimilarity}");
                            }
                            index++;
                        }
                    }
                }
            }
            Console.WriteLine($"Total Results: {response.TotalCount}");
        }

        internal static async Task SetupIndexAsync(Configuration configuration, SearchIndexClient indexClient)
        {
            const string vectorSearchHnswProfile = "my-vector-profile";
            const string vectorSearchHnswConfig = "myHnsw";
            const string vectorSearchVectorizer = "myOpenAIVectorizer";
            const string semanticSearchConfig = "my-semantic-config";

            SearchIndex searchIndex = new(configuration.IndexName)
            {
                VectorSearch = new()
                {
                    Profiles =
                    {
                        new VectorSearchProfile(vectorSearchHnswProfile, vectorSearchHnswConfig)
                        {
                            VectorizerName = vectorSearchVectorizer
                        }
                    },
                    Algorithms =
                    {
                        new HnswAlgorithmConfiguration(vectorSearchHnswConfig)
                    },
                    Vectorizers =
                    {
                        new AzureOpenAIVectorizer(vectorSearchVectorizer)
                        {
                            Parameters = new AzureOpenAIVectorizerParameters
                            {
                                ResourceUri = new Uri(configuration.AzureOpenAIEndpoint),
                                ModelName = configuration.AzureOpenAIEmbeddingModel,
                                DeploymentName = configuration.AzureOpenAIEmbeddingDeployment
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
                        VectorSearchDimensions = int.Parse(configuration.AzureOpenAIEmbeddingDimensions),
                        VectorSearchProfileName = vectorSearchHnswProfile
                    },
                    new SearchField("contentVector", SearchFieldDataType.Collection(SearchFieldDataType.Single))
                    {
                        IsSearchable = true,
                        VectorSearchDimensions = int.Parse(configuration.AzureOpenAIEmbeddingDimensions),
                        VectorSearchProfileName = vectorSearchHnswProfile
                    },
                    new SearchableField("category") { IsFilterable = true, IsSortable = true, IsFacetable = true }
                }
            };

            await indexClient.CreateOrUpdateIndexAsync(searchIndex);
        }

        internal static async Task UploadSampleDocumentsAsync(Configuration configuration, SearchClient searchClient, string sampleDocumentsPath)
        {
            string sampleDocumentContent = File.ReadAllText(sampleDocumentsPath);
            var sampleDocuments = JsonSerializer.Deserialize<List<Dictionary<string, object>>>(sampleDocumentContent);

            var options = new SearchIndexingBufferedSenderOptions<Dictionary<string, object>>
            {
                KeyFieldAccessor = (o) => o["id"].ToString()
            };
            using SearchIndexingBufferedSender<Dictionary<string, object>> bufferedSender = new(searchClient, options);
            await bufferedSender.UploadDocumentsAsync(sampleDocuments);
            await bufferedSender.FlushAsync();
        }

        /// <summary>
        /// Generates embeddings for sample documents and saves the output to a specified path.
        /// </summary>
        /// <param name="configuration">The configuration settings for the Azure OpenAI service.</param>
        /// <param name="azureOpenAIClient">The AzureOpenAIClient instance for embedding generation.</param>
        /// <param name="inputSampleDocumentPath">The file path of the input sample document containing JSON content.</param>
        /// <param name="outputSampleDocumentPath">The file path where the output with embeddings will be saved.</param>
        internal static async Task GenerateAndSaveSampleDocumentsAsync(Configuration configuration, AzureOpenAIClient azureOpenAIClient, string inputSampleDocumentPath, string outputSampleDocumentPath)
        {
            string sampleDocumentContent = File.ReadAllText(inputSampleDocumentPath);
            var sampleDocuments = JsonSerializer.Deserialize<List<Dictionary<string, object>>>(sampleDocumentContent);

            EmbeddingClient embeddingClient = azureOpenAIClient.GetEmbeddingClient(configuration.AzureOpenAIEmbeddingDeployment);
            var embeddingOptions = new EmbeddingGenerationOptions { Dimensions = int.Parse(configuration.AzureOpenAIEmbeddingDimensions) };
            foreach (Dictionary<string, object> sampleDocument in sampleDocuments)
            {
                string title = sampleDocument["title"]?.ToString() ?? string.Empty;
                string content = sampleDocument["content"]?.ToString() ?? string.Empty;

                OpenAIEmbedding titleEmbedding = await embeddingClient.GenerateEmbeddingAsync(title, embeddingOptions);
                OpenAIEmbedding contentEmbedding = await embeddingClient.GenerateEmbeddingAsync(content, embeddingOptions);

                sampleDocument["titleVector"] = titleEmbedding.ToFloats();
                sampleDocument["contentVector"] = contentEmbedding.ToFloats();
            }

            string serializedSampleDocuments = JsonSerializer.Serialize(sampleDocuments);
            File.WriteAllText(outputSampleDocumentPath, serializedSampleDocuments);
        }
    }
}
