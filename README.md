# Vector search (private preview) - Azure Cognitive Search

Welcome to the private preview of the vector search feature in Azure Cognitive Search! When done correctly, vector search is a proven technique for significantly increasing the semantic relevance of search results. By participating in this private preview, you can help us improve our implementation of this feature by [providing your feedback and suggestions](#contact-us).

Cognitive Search can index vectors, but it doesn't generate them. The documents that you push to your search service must contain vectors within the payload. Alternatively, you can use the Indexer to pull vectors from your data sources such as Blob Storage JSON files or CSVs.

To create vectorized data, you can use any embedding model, but we recommend Azure OpenAI or Cognitive Services for images. The Python and JavaScript samples in this repository call Azure OpenAI to generate text embeddings. You can request [access to Azure OpenAI](https://aka.ms/oai/access) in your Azure subscription to use the demo samples we've provided.

## Pricing

This private preview requires billable resources. You'll need to cover the cost of running Azure Cognitive Search, as well as Azure OpenAI if you choose to use their embedding models.

+ [Azure Cognitive Search pricing](https://azure.microsoft.com/pricing/details/search/#pricing) (see also [Plan and manage costs](https://learn.microsoft.com/azure/search/search-sku-manage-costs)).

+ [Azure OpenAI pricing](https://azure.microsoft.com/pricing/details/cognitive-services/openai-service/)

## Get started

For this private preview, we've enabled vector search support in all Azure Cognitive Search regions and all tiers except Free.

You can use an existing search service in a supported tier and region, but you must create a new index.

### 1 - Setup

If you fork or clone this repo, help us protect the private preview status of this feature by making sure your forked and cloned repositories remain private.

To verify feature availability, issue a REST call that creates a new vector search index using the new preview REST API. A successful response confirms feature availability.

```http
POST https://{{YOUR-SEARCH-SERVICE-NAME}}.search.windows.net/indexes?api-version=2023-07-01-preview
  Content-Type: application/json
  api-key: {{YOUR-ADMIN-API-KEY}}
    {  
      "name": "do-i-have-vector-search",
      "fields": [
        {
          "name": "id",
          "type": "Edm.String",
          "key": true
        },
        {  
          "name": "MyVectorField",
          "type": "Collection(Edm.Single)",
          "searchable": true,
          "filterable": false,
          "sortable": false,
          "facetable": false,
          "retrievable": true,
          "analyzer": "",
          "dimensions": 5,
          "algorithmConfiguration": "vectorConfig"
        }
      ],
        "vectorSearch": {
            "algorithmConfigurations": [
                {
                    "name": "vectorConfig",
                    "algorithm": "hnsw"
                }
            ]
        }
    }
```

### 2 - Demos

We provide three demo solutions to get you started.

| Sample | Purpose | Description |
|--------|---------|-------------|
| Python | Creates vector representations of images or text | A notebook that calls OpenAI to create vectorized data. We used this notebook to create the sample data for the demo index. You can revise your copy of the notebook to test vector search with other data and your own schemas. See the [sample readme](/demo-python/demo-python/readme.md) for instructions on notebook setup. |
| JavaScript| Creates vector representations of images or text | A node.js version of the Python sample. See the [sample readme](/demo-javascript/readme.md) for instructions on sample setup. |
| Postman collection | Create, load, and query a search index that contains text and vector fields. | A collection of REST API calls to an Azure Cognitive Search instance. The requests in this collection include an index schema, sample documents, and sample queries. The collection is documented in [Quickstart: Vector search](/docs/vector-search-quickstart.md). Each query demonstrates key scenarios. <p>Use the [Postman app](https://www.postman.com/downloads/) and import the collection.</p> <p>Set collection variables to provide your search service URI and admin key</p> If you're unfamiliar with Postman, see this [Postman/REST quickstart for Cognitive Search](https://learn.microsoft.com/azure/search/search-get-started-rest).|

## 3 - Quickstart

For your first experience with the end-to-end workflow, begin with the [vector search quickstart](/docs/vector-search-quickstart.md). It takes you through a series of HTTP requests that create, load, and query an index. You'll find combinations of vector-only search, hybrid search, vectors with filters, and so on.

Sample data can be found in the Upload Docs request. It consists of 108 documents about Azure services and includes vectorized data created from demo code.

1. Import the collection into Postman.
1. In collection variables, provide your search service URI, an admin API key, an index name.
1. Run each request in sequence using API version: **2023-07-01-preview**.

## 4 - Try it with your data

When you're ready to extend the quickstart or adapt the collection to you data, you'll need to:

+ Create vector representations for specific fields. Choose fields that have semantic value, such as descriptions or summaries. You can use either the [Python demo](/demo-python/) or [JavaScript demo](/demo-javascript/) to generate embeddings. To use the demos as-is, you'll need [Azure OpenAI](https://aka.ms/oai/access) in your subscription.

+ Create, load, and query your custom index. Use the **2023-07-01-preview** REST API for these operations. We recommend Postman or a similar tool for proof-of-concept testing.

## Private preview limitations

+ This feature is only available via indexes and queries that target **2023-07-01-preview** REST API. There is no Azure SDK support and no portal support. If you view or query a search index that has vector fields, the portal treats them as strings and any queries will be scored using BM25.

  Your new index must be created using the new preview API, and your queries must target the preview API. You can't use vector search with existing indexes.

+ Your search service must be a billable tier. Although the search service is billable, there is no additional charge for the vector search feature.

+ Service and subscription limits haven't been finalized, but the [API request limits](https://learn.microsoft.com/azure/search/search-limits-quotas-capacity#api-request-limits) do apply. Request payloads cannot exceed 8K for URIs or 16 MB for the request body. The following additional limits apply to this preview:

  + Maximum number of vectors fields per index: None. However, please keep in mind the vector float limit and index size limitations per SKU.
  + Maximum number of dimensions: 2048

+ Index definitions are currently subject to the following limitations:

  + Vector fields with complex types or collections of complex types aren't supported.
  + Vector fields can't have filter, facet, or sort attributions.

+ Query definitions are currently subject to these limitations:

  + POST verbs are required. Don't use GET.
  + $count isn't supported.
  + Multi-field vector queries aren't supported. Specifically, you can't set "searchFields" to multiple vector fields.
  + Multi-vector queries aren't supported. For example, the Postman collection has vector fields named TitleVector and ContentVector. Your query can include TitleVector or ContentVector, but not both.
  + Sorting ($orderby) and pagination ($skip) for hybrid queries aren't supported.

+ There is no official public documentation or samples beyond what you'll find in this private repository. Please contact us with any questions or concerns.

## Storage and usage limits

| SKU	| Storage quota (GB)| Floats limit per partition (1e6) |
|--|--|--|
| Basic | 2 | 100 |
| S1 | 25 | 250 |
| S2 | 100 | 1000 |
| S3 | 200 | 2000 |
| L1 | 1000 | 2000 |
| L2 | 2000 | 6000 |

## Contact us

For questions, concerns, or other feedback about vector search, please reach out to azuresearch_contact@microsoft.com.

For suggestions about docs or samples, please file a pull request or issue on this repo, or email us with your requests.

## Documentation

For the private preview, we're providing the following documentation:

+ This readme covers installation and introduces you to the private preview.
+ This [FAQ](/docs/faq.md) answers basic questions about feature capabilities.
+ Python and JavaScript demos have readme files for setting up and running the demo code. 
+ REST API reference in the [/docs folder](/docs/rest-api-reference/rest-api-reference.md).
+ Concept docs and How-to's for the main scenarios can be found in the [/docs folder](/docs/).
+ For updates to features and samples, see this [change list](changelist.md)
