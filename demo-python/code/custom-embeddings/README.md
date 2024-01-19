# Custom Embeddings Sample

This sample demonstrates how to deploy a custom embedding model to Azure Functions. This function is used as a [custom vectorizer](https://learn.microsoft.com/azure/search/vector-search-how-to-configure-vectorizer) to automatically [vectorize queries](https://learn.microsoft.com/azure/search/vector-search-overview) for Azure Search. An [indexer](https://learn.microsoft.com/azure/search/search-howto-create-indexers) with a [skillset](https://learn.microsoft.com/azure/search/cognitive-search-defining-skillset) uses the [Split Skill](https://learn.microsoft.com/azure/search/cognitive-search-skill-textsplit) to automatically chunk documents in a [blob data source](https://learn.microsoft.com/azure/search/search-howto-indexing-azure-blob-storage) and vectorizes those chunks using the custom embedding model.

## Prerequisites
1. Install [python](https://learn.microsoft.com/windows/python/beginners)
1. Install [azd](https://learn.microsoft.com/azure/developer/azure-developer-cli/overview)
1. Install [vscode](https://code.visualstudio.com/download)

## Setup
1. Run `azd up` inside the directory to provision the sample
1. Open the [notebook](./azure-search-custom-vectorization-sample.ipynb) to run sample queries once the sample is provisioned and the indexer has finished running.

## Using an already existing search service
1. Before running `azd up`, set the following `azd` env vars:
1. `azd env set AZURE_SEARCH_SERVICE <your-search-service-name>`
1. `azd env set AZURE_SEARCH_SERVICE_LOCATION <your-search-service-location>`
1. `azd env set AZURE_SEARCH_SERVICE_RESOURCE_GROUP <your-search-service-resource-group>`
1. `azd env set AZURE_SEARCH_SERVICE_SKU <your-search-service-sku>`