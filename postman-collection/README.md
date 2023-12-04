---
page_type: sample
languages:
  - rest
name: "Vector REST APIs for Azure AI Search"
description: |
  Demonstrates generally available and preview REST APIs for indexing and querying vectors in Azure AI Search.
products:
  - azure
  - azure-cognitive-search
urlFragment: rest-api-vectors
---

# Vector REST APIs for Azure AI Search

![Flask sample MIT license badge](https://img.shields.io/badge/license-MIT-green.svg)

Use Postman and the Azure AI Search REST APIs to work with vector and hybrid queries.

There are two collections:

+ Generally available version (2023-11-01) demonstrates vector indexing and queries.

+ Preview version (2023-10-01-preview) adds integrated vectorization, with data chunking and embedded calls to Azure OpenAI. This worflow adds an indexer, data source, and skillset. It uses sample PDFs that you upload to Azure Storage to demonstrate data chunking.

## Prerequisites

+ [Postman Desktop app](https://www.getpostman.com/)
+ [Azure AI Search service](https://docs.microsoft.com/azure/search/search-create-service-portal)
+ (optional) [Semantic ranking](https://learn.microsoft.com/azure/search/semantic-how-to-enable-disable) if you want to run the hybrid query that invokes semantic ranking
+ (optional) [Azure OpenAI](https://learn.microsoft.com/azure/ai-services/openai/how-to/create-resource) with a deployment of **text-embedding-ada-002** if you want to generate embeddings (the sample comes with vectors, so prerequisite is only needed if you want different vectors.)
+ (optional) [Azure Storage](https://learn.microsoft.com/azure/storage/blobs/) for the preview API workflow.

## Setup

1. Clone or download this sample repository.
1. Extract contents if the download is a zip file. Make sure the files are read-write.

### Import and set collection variables

1. For the preview collection only, upload the [sample health plan PDFs](https://github.com/Azure-Samples/azure-search-sample-data/tree/main/health-plan) to a blob container on Azure Storage. Make a note of the container name and a connection string so that you can provide these values as variables.
1. Start Postman and import either one of the collections.
1. Select the collection, open the actions menu, select **Edit**.
1. Enter variables:
   + Index or prefix name to apply a naming convention to the created objects.
   + Search service name and an admin API key, which you can [obtain from the Azure portal](https://learn.microsoft.com/azure/search/search-get-started-vectors#copy-a-key-and-url).
   + Azure OpenAI service name, key, REST API version, and model deployment name.
   + For the preview collection, provide an Azure Storage blob container name and connection string.
1. Select **Save**.
1. Send each request to the service.

## Next steps

You can learn more about Azure AI Search on the [official documentation site](https://docs.microsoft.com/azure/search).
