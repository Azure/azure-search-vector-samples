using Azure.Search.Documents;
using Azure.Search.Documents.Indexes;
using Azure.Search.Documents.Indexes.Models;
using QuantizationAndStorageOptions;
using Azure.Identity;
using Azure;

using Microsoft.Extensions.Configuration;

using System.IO;
using System.Text.Json;

var configuration = new Configuration();
new ConfigurationBuilder()
    .SetBasePath(Directory.GetCurrentDirectory())
    .AddEnvironmentVariables()
    .AddJsonFile("local.settings.json")
    .Build()
    .Bind(configuration);

configuration.Validate();
var defaultCredential = new DefaultAzureCredential();
var searchIndexClient = InitializeSearchIndexClient(configuration, defaultCredential);

string baseIndexName = configuration.IndexName;

string dataPath = Path.Join("..", "..", "data", "documentVectors.json");
string jsonString = File.ReadAllText(dataPath);
Document[] documents = JsonSerializer.Deserialize<Document[]>(jsonString);

string baselineIndexName = $"{baseIndexName}-baseline";
CreateAndInitializeIndex(
    CreateStorageIndex(
        baselineIndexName,
        useFloat16: false,
        noStored: false,
        useQuantization: false),
    searchIndexClient,
    documents);

string narrowIndexName = $"{baseIndexName}-narrow";
CreateAndInitializeIndex(
    CreateStorageIndex(
        narrowIndexName,
        useFloat16: true,
        noStored: false,
        useQuantization: false),
    searchIndexClient,
    documents);

string quantizationIndexName = $"{baseIndexName}-quantization";
CreateAndInitializeIndex(
    CreateStorageIndex(
        quantizationIndexName,
        useFloat16: false,
        noStored: false,
        useQuantization: true),
    searchIndexClient,
    documents);

string storedIndexName = $"{baseIndexName}-stored";
CreateAndInitializeIndex(
    CreateStorageIndex(
        storedIndexName,
        useFloat16: false,
        noStored: true,
        useQuantization: false),
    searchIndexClient,
    documents);

string allIndexName = $"{baseIndexName}-all";
CreateAndInitializeIndex(
    CreateStorageIndex(
        allIndexName,
        useFloat16: true,
        noStored: true,
        useQuantization: true),
    searchIndexClient,
    documents);

SearchIndexClient InitializeSearchIndexClient(Configuration configuration, DefaultAzureCredential defaultCredential)
{
    if (!string.IsNullOrEmpty(configuration.AdminKey))
    {
        return new SearchIndexClient(new Uri(configuration.ServiceEndpoint), new AzureKeyCredential(configuration.AdminKey));
    }

    return new SearchIndexClient(new Uri(configuration.ServiceEndpoint), defaultCredential);
}

SearchIndex CreateStorageIndex(string indexName, bool useFloat16, bool noStored, bool useQuantization) 
{
    const string vectorSearchHnswProfile = "my-vector-profile";
    const string vectorSearchHnswConfig = "myHnsw";
    const int modelDimensions = 3072;

    SearchFieldDataType dataType;
    if(useFloat16)
    {
        dataType = SearchFieldDataType.Collection(SearchFieldDataType.Half);
    }
    else
    {
        dataType = SearchFieldDataType.Collection(SearchFieldDataType.Single);
    }

    SearchIndex searchIndex = new(indexName)
    {
        VectorSearch = new()
        {
            Profiles =
            {
                new VectorSearchProfile(vectorSearchHnswProfile, vectorSearchHnswConfig)
                {
                    CompressionConfigurationName = useQuantization ? "my-compression" : null
                }
            },
            Algorithms =
            {
                new HnswAlgorithmConfiguration(vectorSearchHnswConfig),
            }
        },
        SemanticSearch = new()
        {
            Configurations =
            {
                new SemanticConfiguration("semantic-config", new()
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
            new SearchableField("id") { IsKey = true, IsFilterable = true, IsSortable = true },
            new SearchableField("title"),
            new SearchableField("chunk"),
            new SearchField("embedding", dataType)
            {
                IsSearchable = true,
                IsHidden = noStored,
                IsStored = !noStored,
                VectorSearchDimensions = modelDimensions,
                VectorSearchProfileName = vectorSearchHnswProfile
            }
        },
    };

    if (useQuantization)
    {
        searchIndex.VectorSearch.Compressions.Add(new ScalarQuantizationCompressionConfiguration("my-compression"));
    }

    return searchIndex;
}

void CreateAndInitializeIndex(SearchIndex index, SearchIndexClient indexClient, Document[] documents)
{
    Console.WriteLine($"Creating index {index.Name}");
    indexClient.CreateOrUpdateIndex(index);
    var searchClient = indexClient.GetSearchClient(index.Name);
    using var bufferedSender = new SearchIndexingBufferedSender<Document>(searchClient);
    bufferedSender.UploadDocuments(documents);
}

class Document
{
    public string id { get; set; }
    public string title { get; set; }
    public string chunk { get; set; }
    public float[] embedding { get; set; }
}