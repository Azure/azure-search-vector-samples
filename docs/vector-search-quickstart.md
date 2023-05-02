# Quickstart: Vector search

Use this article to get started with vector search using Azure Cognitive Search REST APIs that create, load, and query a search index. 

## About the sample data and queries

Sample data consists of text and vector descriptions of 108 Azure services, generated from ChatGPT in Azure OpenAI.

+ Textual data is used for keyword search, semantic ranking, and capabilities that currently depend on text (filters, facets, and sorting). 

+ Vector data (text embeddings) is used for vector search. The vectors used for queries and to populate the titleVector and contentVector fields were generated separately and copied into the payload of the Upload Docs request and into the queries.

Vector data was generated through demo code in [Python](../demo-python/) (or [JavaScript](../demo-javascript/)), calling Azure OpenAI for the embeddings. The output is provided for you in this quickstart in the Upload Documents request so that you can skip that step and focus on the mechanics of indexing and query setup.

For vector queries, *we've provided the embeddings for every query input*, but you can optionally generate your own vector queries using the "Create Query Embedding" request. If you opt-in for this step, you'll need to provide Azure OpenAI model and connection information. The embedding model must be identical to the one used to generate embeddings in your search corpus. For this quickstart, that embedding model is **text-embedding-ada-002**, API version **2022-12-01**.

## Prerequisites

+ [Postman app](https://www.postman.com/downloads/)

+ An Azure subscription. [Create one for free](https://azure.microsoft.com/free/).

+ Azure Cognitive Search service (any region, any tier but free). However, to run the last two queries, S1 or higher is required, with [semantic search enabled](https://learn.microsoft.com/azure/search/semantic-search-overview#enable-semantic-search).

+ [Sample Postman collection](/postman-collection/), with requests targeting the **2023-07-01-preview** API version of Azure Cognitive Search.

+ Optional "Create Query Embeddings" request: you'll need [Azure OpenAI](https://aka.ms/oai/access) with a deployment of **text-embedding-ada-002**. Provide the Azure OpenAI endpoint, key, model deployment name, and API version in the collection variables.

## Set up your project

1. Fork or clone the repository.

1. Start Postman and import the collection.

1. Edit the collection's variables to use your search service name, API key, and index name.

You're now ready to send the requests to your search service.

## Create an index

Use the [Create or Update Index](/docs/rest-api-reference/create-or-update-index.md) REST API for this request.

The index schema is organized around a product catalog scenario. Sample data consists of titles, categories, and descriptions of 108 Azure services. This schema includes fields for vector and traditional keyword search, with configurations for vector and semantic search.

```http
PUT https://{{search-service-name}}.search.windows.net/indexes/{{index}}?api-version={{api-version}}
Content-Type: application/json
api-key: {{admin-api-key}}
{
    "name": "{{index}}",
    "fields": [
        {
            "name": "id",
            "type": "Edm.String",
            "key": true,
            "filterable": true
        },
        {
            "name": "category",
            "type": "Edm.String",
            "filterable": true,
            "searchable": true,
            "retrievable": true
        },
        {
            "name": "title",
            "type": "Edm.String",
            "searchable": true,
            "retrievable": true
        },
        {
            "name": "titleVector",
            "type": "Collection(Edm.Single)",
            "searchable": true,
            "retrievable": true,
            "dimensions": 1536,
            "vectorSearchConfiguration": "vectorConfig"
        },
        {
            "name": "content",
            "type": "Edm.String",
            "searchable": true,
            "retrievable": true
        },
        {
            "name": "contentVector",
            "type": "Collection(Edm.Single)",
            "searchable": true,
            "retrievable": true,
            "dimensions": 1536,
            "vectorSearchConfiguration": "vectorConfig"
        }
    ],
    "corsOptions": {
        "allowedOrigins": [
            "*"
        ],
        "maxAgeInSeconds": 60
    },
    "vectorSearch": {
        "algorithmConfigurations": [
            {
                "name": "vectorConfig",
                "kind": "hnsw"
            }
        ]
    },
    "semantic": {
        "configurations": [
            {
                "name": "my-semantic-config",
                "prioritizedFields": {
                    "titleField": {
                        "fieldName": "title"
                    },
                    "prioritizedContentFields": [
                        {
                            "fieldName": "content"
                        }
                    ],
                    "prioritizedKeywordsFields": []
                }
            }
        ]
    }
}
```

You should get a status HTTP 201 success.

### Key points:

+ The "fields" collection includes a required key field, a category field, and pairs of fields (such as "title", "titleVector") for keyword and vector search. Co-locating vector and non-vector fields in the same index enables hybrid queries. For instance, you can combine filters, keyword search with semantic ranking, and vectors into a single query operation.

+ Vector fields must be `"type": "Collection(Edm.Single)"` with `"dimensions"` and `"vectorSearchConfiguration"` properties. See [this article](rest-api-reference/create-or-update-index.md) for property descriptions.

+ The "vectorSearch" configuration is an array of algorithms, but only the "hnsw" algorithm is supported in this preview. Hierarchical Navigable Small World (HNSW) is part of the infrastructure that powers Azure Cognitive Search. It works well with [embedding models](https://learn.microsoft.com/azure/cognitive-services/openai/concepts/models#embeddings-models) provided in Azure OpenAI.

+ The "semanticSearch" configuration enables semantic re-ranking of search results. You can semantically re-rank results in queries of type "semantic" for string fields that are specified in the configuration.

## Upload documents

Use the [Add, Update, or Delete Documents](/docs/rest-api-reference/upload-documents.md) REST API for this request.

For readability, the following example show a subset of documents and embeddings. The body of the Upload Documents request consists of 108 documents, each with a full set of embeddings for "titleVector" and "contentVector".

```http
POST https://{{search-service-name}}.search.windows.net/indexes/{{index-name}}/docs/index?api-version={{api-version}}
Content-Type: application/json
api-key: {{admin-api-key}}
{
    "value": [
        {
            "id": "1",
            "title": "Azure App Service",
            "content": "Azure App Service is a fully managed platform for building, deploying, and scaling web apps. You can host web apps, mobile app backends, and RESTful APIs. It supports a variety of programming languages and frameworks, such as .NET, Java, Node.js, Python, and PHP. The service offers built-in auto-scaling and load balancing capabilities. It also provides integration with other Azure services, such as Azure DevOps, GitHub, and Bitbucket.",
            "category": "Web",
            "titleVector": [
                -0.02250031754374504,
                 . . . 
                        ],
            "contentVector": [
                -0.024740582332015038,
                 . . .
            ],
            "@search.action": "upload"
        },
        {
            "id": "2",
            "title": "Azure Functions",
            "content": "Azure Functions is a serverless compute service that enables you to run code on-demand without having to manage infrastructure. It allows you to build and deploy event-driven applications that automatically scale with your workload. Functions support various languages, including C#, F#, Node.js, Python, and Java. It offers a variety of triggers and bindings to integrate with other Azure services and external services. You only pay for the compute time you consume.",
            "category": "Compute",
            "titleVector": [
                -0.020159931853413582,
                . . .
            ],
            "contentVector": [
                -0.02780858241021633,,
                 . . .
            ],
            "@search.action": "upload"
        }
        . . .
    ]
}
```

### Key points:

+ Documents in the payload consist of fields defined in the index schema. 

+ Vector fields can hold a maximum of 2014 embeddings each, and contain floating point values. The maximum number of embeddings is determined by the output dimensions of the model you're using. In this case, the maximum output dimensions of **text-embedding-ada-002** is 1536.

## Run queries

Use the [Search Documents](/docs/rest-api-reference/search-documents.md) REST API for this request. Recall that the private preview has [several limitations](../README.MD#private-preview-limitations) related to queries:

+ POST is required for this preview and the API version must be 2023-07-01-Preview
+ Only one vector field per query at this time (for example, either "titleVector" or "contentVector", but not both)
+ Multi-vector queries aren't supported. A search request can carry a single vector query.
+ Sorting ($orderby) and pagination ($skip) are not supported for hybrid queries.
+ Facets ($facet) and count ($count) are not supported for vector and hybrid queries.

There are 6 queries to demonstrate the patterns. We use the same query string (*"what azure services support full text search"*) across all of them so that you can compare results and relevance.

+ [Single vector search](#single-vector-search)
+ [Single vector search with filter](#single-vector-search-with-filter)
+ [Simple hybrid search](#simple-hybrid-search)
+ [Simple hybrid search with filter](#simple-hybrid-search-with-filter)
+ [Semantic hybrid search](#semantic-hybrid-search)
+ [Semantic hybrid search with filter](#semantic-hybrid-search-with-filter)

### Single vector search

In this vector query, which is shortened for brevity, the "value" contains the vectorized text of the query input, "fields" determines which vector fields are searched, and "k" specifies the number of nearest neighbors to return as top hits.

Recall that the vector query was generated from this string: "what azure services support full text search". The search targets the "contentVector" field.

```http
POST https://{{search-service-name}}.search.windows.net/indexes/{{index-name}}/docs/search?api-version={{api-version}}
Content-Type: application/json
api-key: {{admin-api-key}}
{
    "vector": {
        "value": [
            -0.009154141,
            0.018708462,
            . . . 
            -0.02178128,
            -0.00086512347
        ],
        "fields": "contentVector",
        "k": 5
    },
    "select": "title, content, category"
}
```

The response will include 5 matches, and each result provides a search score, title, content, and category. In a similarity search, the response will always include "k" matches, although the search score will be quite low if the similarity is weak.

### Single vector search with filter

You can add filters, but the filters are applied to the non-vector content in your index. In this example, the filter applies to the "category" field.

The response is 10 Azure services, with a search score, title, and category for each one.

```http
POST https://{{search-service-name}}.search.windows.net/indexes/{{index-name}}/docs/search?api-version={{api-version}}
Content-Type: application/json
api-key: {{admin-api-key}}
{
    "vector": {
        "value": [
            -0.009154141,
            0.018708462,
            . . . 
            -0.02178128,
            -0.00086512347
        ],
        "fields": "contentVector",
        "k": 10
    },
    "select": "title, category",
    "filter": "category eq 'Databases'"
}
```

### Simple hybrid search

Hybrid search instructs the search engine to search over both the vector indices and the inverted indices of your search index. Hybrid queries work when your index includes both vector fields and regular search fields (strings, numeric data, geo coordinates, and so forth).

For best results, vector "value" and "search" should be equivalent (i.e., vector "value" should be an embedding of whatever text is in "search"). If the queries are different, the queries are OR'd.

The response includes the top 10 by search score. Both vector queries and free text queries are assigned a search score. The scores are merged using Reciprocal Rank Fusion (RRF) to weight each document with the inverse of its position on the rank. 

```http
POST https://{{search-service-name}}.search.windows.net/indexes/{{index-name}}/docs/search?api-version={{api-version}}
Content-Type: application/json
api-key: {{admin-api-key}}
{
    "vector": {
        "value": [
            -0.009154141,
            0.018708462,
            . . .
            -0.02178128,
            -0.00086512347
        ],
        "fields": "contentVector",
        "k": 10
    },
    "search": "what azure services support full text search",
    "select": "title, content, category",
    "top": "10"
}
```

Compare the responses between Single Vector Search and Simple Hybrid Search for the top result. The different ranking algorithms produce scores that have different magnitudes.

**Single Vector Search**: Using Hierarchical Navigable Small Worlds (hnsw) for ranking

```
{
    "@search.score": 0.8851871,
    "title": "Azure Cognitive Search",
    "content": "Azure Cognitive Search is a fully managed search-as-a-service that enables you to build rich search experiences for your applications. It provides features like full-text search, faceted navigation, and filters. Azure Cognitive Search supports various data sources, such as Azure SQL Database, Azure Blob Storage, and Azure Cosmos DB. You can use Azure Cognitive Search to index your data, create custom scoring profiles, and integrate with other Azure services. It also integrates with other Azure services, such as Azure Cognitive Services and Azure Machine Learning.",
    "category": "AI + Machine Learning"
},
```

**Simple Hybrid Search**: Using Reciprocal Rank Fusion for ranking

```
{
    "@search.score": 0.03333333507180214,
    "title": "Azure Cognitive Search",
    "content": "Azure Cognitive Search is a fully managed search-as-a-service that enables you to build rich search experiences for your applications. It provides features like full-text search, faceted navigation, and filters. Azure Cognitive Search supports various data sources, such as Azure SQL Database, Azure Blob Storage, and Azure Cosmos DB. You can use Azure Cognitive Search to index your data, create custom scoring profiles, and integrate with other Azure services. It also integrates with other Azure services, such as Azure Cognitive Services and Azure Machine Learning.",
    "category": "AI + Machine Learning"
},
```

### Simple hybrid search with filter

This example adds a filter, which is applied to the non-vector content of the search index.

```http
POST https://{{search-service-name}}.search.windows.net/indexes/{{index-name}}/docs/search?api-version={{api-version}}
Content-Type: application/json
api-key: {{admin-api-key}}
{
    "vector": {
        "value": [
            -0.009154141,
            0.018708462,
            . . . 
            -0.02178128,
            -0.00086512347
        ],
        "fields": "contentVector",
        "k": 10
    },
    "search": "what azure services support full text search",
    "select": "title, content, category",
    "filter": "category eq 'Databases'",
    "top": "10"
}
```

### Semantic hybrid search

Assuming that you've [enabled semantic search](https://learn.microsoft.com/azure/search/semantic-search-overview#enable-semantic-search) and your index definition includes a [semantic configuration](https://learn.microsoft.com/azure/search/semantic-how-to-query-request?tabs=portal%2Cportal-query), you can formulate a query that includes vector search, plus keyword search with semantic ranking, caption, answers, and spell check.

```http
POST https://{{search-service-name}}.search.windows.net/indexes/{{index-name}}/docs/search?api-version={{api-version}}
Content-Type: application/json
api-key: {{admin-api-key}}
{
    "vector": {
        "value": [
            -0.009154141,
            0.018708462,
            . . . 
            -0.02178128,
            -0.00086512347
        ],
        "fields": "contentVector",
        "k": 10
    },
    "search": "what azure services support full text search",
    "select": "title, content, category",
    "queryType": "semantic",
    "semanticConfiguration": "my-semantic-config",
    "queryLanguage": "en-us",
    "captions": "extractive",
    "answers": "extractive",
    "top": "10"
}
```

### Semantic hybrid search with filter

Here's the last query in the collection. It's the same hybrid query as above, with a filter.

```http
POST https://{{search-service-name}}.search.windows.net/indexes/{{index-name}}/docs/search?api-version={{api-version}}
Content-Type: application/json
api-key: {{admin-api-key}}
{
    "vector": {
        "value": [
            -0.009154141,
            0.018708462,
            . . . 
            -0.02178128,
            -0.00086512347
        ],
        "fields": "contentVector",
        "k": 10
    },
    "search": "what azure services support full text search",
    "select": "title, content, category",
    "queryType": "semantic",
    "semanticConfiguration": "my-semantic-config",
    "queryLanguage": "en-us",
    "captions": "extractive",
    "answers": "extractive",
    "filter": "category eq 'Databases'",
    "top": "10"
}
```

### Key points:

+ Vector search is specified through the vector "vector.value" property. Keyword search is specified through "search" property.

+ In a hybrid search, you can integrate vector search with full text search over keywords. Filters, spell check, and semantic ranking apply to textual content only, and not vectors. In this final query, there is no semantic "answer" because the system didn't produce one that was sufficiently strong.

## Clean up

Azure Cognitive Search is a billable resource. If it's no longer needed, delete it from your subscription to avoid charges.

## Next steps

As a next step, we recommend reviewing the demo code for either [Python](../demo-python/) or [JavaScript](../demo-javascript/) to understand how embeddings are generated.
