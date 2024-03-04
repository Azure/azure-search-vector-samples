# Readme for custom-embeddings demo

This end-to-end sample demonstrates how to deploy [SentenceTransformers](https://www.sbert.net/) as a custom embedding model that runs in an Azure function app. This function is used as a [custom vectorizer](https://learn.microsoft.com/azure/search/vector-search-how-to-configure-vectorizer) to automatically [vectorize queries](https://learn.microsoft.com/azure/search/vector-search-overview) on Azure AI Search.

All resources and sample data are deployed automatically, resulting in a populated vector index that's ready to query.

This sample uses [indexer-based indexing](https://learn.microsoft.com/azure/search/search-howto-create-indexers) with a [skillset](https://learn.microsoft.com/azure/search/cognitive-search-defining-skillset) having a [Text Split skill](https://learn.microsoft.com/azure/search/cognitive-search-skill-textsplit) to automatically chunk documents in a [blob data source](https://learn.microsoft.com/azure/search/search-howto-indexing-azure-blob-storage). The code vectorizes those chunks using the custom embedding model.

## Prerequisites

+ [azd](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd), used to deploy all Azure resources and assets used in this sample.

This sample uses the [Azure Python SDK](https://learn.microsoft.com/en-us/python/api/azure-search-documents/?view=azure-python-preview) for indexing and vector query operations.

## Set variables and run the script

This sample uses [`azd`](https://learn.microsoft.com/azure/developer/azure-developer-cli/) and a bicep template to deploy all Azure resources, including Azure AI Search. To use an existing search service, set environment variables before running `azd up`.

1. Open a command line prompt at the sample folder (custom-vectorizer).

1. Optionally, enter variables if you have an existing search service:

   + `azd env set AZURE_SEARCH_SERVICE <your-search-service-name>`. Provide just the service name.
   + `azd env set AZURE_SEARCH_SERVICE_LOCATION <your-search-service-region>`. Provide a quote-enclosed string if using a full name, such as "West US2".
   + `azd env set AZURE_SEARCH_SERVICE_RESOURCE_GROUP <your-search-service-resource-group>`. 
   + `azd env set AZURE_SEARCH_SERVICE_SKU <your-search-service-sku>`. Valid values are case-sensitive: `basic`, `standard`, `standard2`, `standard3`,`storage_optimized_l1`, `storage_optimized_l2`

1. Run `azd up`.

   + Choose your Azure subscription.
   + Enter a development environment name.
   + Enter a region for the function app. 

   If you aren't prompted for an environment or region, retry `azd env new` to specify a new environment.

   The deployment creates multiple Azure resources and runs multiple jobs. It takes several minutes to complete. 

1. Open the [notebook](./azure-search-custom-vectorization-sample.ipynb) to run sample queries once the sample is provisioned and the indexer has finished running.

1. If you can't run the queries, check your search service to make sure the index, indexer, data source, and skillset exist. Object creation won't occur if your function app isn't fully warmed up when `azd` gets to this step. To create the objects manually, run  `./scripts/setup_search_service.ps1` at the command line prompt.

   You should see the following output statements:

   ```bash
   Create or update sample index custom-embedding-index...
   Create or update sample data source custom-embedding-datasource...
   Create or update sample skillset custom-embedding-skillset
   Create or update sample indexer custom-embedding-indexer
   ```
