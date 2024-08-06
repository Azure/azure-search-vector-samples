# Readme for semantic chunking demo

This end-to-end sample demonstrates how to deploy [Document Intelligence](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/overview?view=doc-intel-4.0.0) for [semantic chunking](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/concept-retrieval-augmented-generation?view=doc-intel-4.0.0) that runs in an Azure function app. This function is used as a [custom skill](https://learn.microsoft.com/en-us/azure/search/cognitive-search-custom-skill-web-api) to automatically convert documents to Markdown and chunk them in Azure AI Search.

All resources and sample data are deployed automatically, resulting in a populated vector index that's ready to query.

This sample uses [indexer-based indexing](https://learn.microsoft.com/azure/search/search-howto-create-indexers) with a [skillset](https://learn.microsoft.com/azure/search/cognitive-search-defining-skillset) having two [custom skills](https://learn.microsoft.com/en-us/azure/search/cognitive-search-custom-skill-web-api) to automatically extract and chunk documents in a [blob data source](https://learn.microsoft.com/azure/search/search-howto-indexing-azure-blob-storage). The code vectorizes those chunks using an Azure OpenAI embedding model.

## Architecture Diagram

![Picture](./media/docintelcustom.png)

## Prerequisites

+ [azd](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd), used to deploy all Azure resources and assets used in this sample.

This sample uses the [Azure Python SDK](https://learn.microsoft.com/en-us/python/api/azure-search-documents/?view=azure-python-preview) for indexing and vector query operations.

## Set variables and run the script

This sample uses [`azd`](https://learn.microsoft.com/azure/developer/azure-developer-cli/) and a bicep template to deploy all Azure resources, including Azure AI Search. To use an existing search service, set environment variables before running `azd up`.

1. Open a command line prompt at the sample folder (custom-vectorizer).

1. Optionally, enter variables if you have an existing search service or Azure OpenAI account:

   + `azd env set AZURE_SEARCH_SERVICE <your-search-service-name>`. Provide just the service name.
   + `azd env set AZURE_SEARCH_SERVICE_LOCATION <your-search-service-region>`. Provide a quote-enclosed string if using a full name, such as "West US2".
   + `azd env set AZURE_SEARCH_SERVICE_RESOURCE_GROUP <your-search-service-resource-group>`. 
   + `azd env set AZURE_SEARCH_SERVICE_SKU <your-search-service-sku>`. Valid values are case-sensitive: `basic`, `standard`, `standard2`, `standard3`,`storage_optimized_l1`, `storage_optimized_l2`
   + `azd env set AZURE_OPENAI_ACCOUNT <your-openai-account>`
   + `azd env set AZURE_OPENAI_EMB_DEPLOYMENT <your-openai-embedding-deployment-name>`
   + `azd env set AZURE_OPENAI_EMB_MODEL <your-openai-embedding-model-name>`
   + `azd env set AUZRE_OPENAI_EMB_MODEL_DIMENSIONS <your-openai-embedding-model-dimensions>`. Only required if you want to use dimensions other than 1536 for `text-embedding-3-large` or `text-embedding-3-small`
   + `azd env set AZURE_OPENAI_LOCATION <your-openai-location>`. Provide a quote-enclosed string if using a full name, such as "West US2"

1. Run `azd up`.

   + Choose your Azure subscription.
   + Enter a development environment name.
   + Enter a region for the function app. 

   If you aren't prompted for an environment or region, retry `azd env new` to specify a new environment.

   The deployment creates multiple Azure resources and runs multiple jobs. It takes several minutes to complete. 

1. Open the [notebook](./document-intelligence-custom-skill.ipynb) to run sample queries once the sample is provisioned and the indexer has finished running.

1. If you can't run the queries, check your search service to make sure the index, indexer, data source, and skillset exist. Object creation won't occur if your function app isn't fully warmed up when `azd` gets to this step. To create the objects manually, run  `./scripts/setup_search_service.ps1` at the command line prompt.

   You should see the following output statements:

   ```bash
   Uploading sample data...
   Getting function URL...
   Create or update sample index document-intelligence-index...
   Create or update sample data source document-intelligence-datasource...
   Create or update sample skillset document-intelligence-skillset
   Create or update sample indexer document-intelligence-indexer
   ```
