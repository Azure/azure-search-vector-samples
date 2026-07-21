---
page_type: sample
languages:
  - python
name: Query rewriting in Python
products:
  - azure
  - azure-cognitive-search
  - azure-openai
description: |
  Using azure-search-documents and the Azure SDK for Python, demonstrate how to use query rewriting to improve your search relevance with hybrid search and Reciprocal Rank Fusion
urlFragment: vector-search-python
---

# Query rewriting using Python (Azure AI Search)  

The Python notebook creates vectorized data on Azure AI Search and demonstrates how a query rewriting technique can be used to search an index, returning output to the notebook.

- Create an index schema
- Load the sample data
- Embed the documents in-memory
- Index the vector and nonvector fields
- Run a hybrid query
- Rewrite the hybrid query for improved relevance
- Combine multiple rewritten queries using a manual Reciprocal Rank Fusion (RRF) calculation
- Combine multiple rewritten queries using an automatic RRF calculation
- Use semantic ranking to further improve relevance

The sample data is a JSON file of 108 descriptions of various Azure services. The descriptions are short, which makes data chunking unnecessary.

The queries are articulated as strings. An Azure OpenAI embedding model converts the strings to vectors at run time. The text query and the vector query are combined at run time to produce a hybrid query.

The sample includes a simple prompt that is used to rewrite the queries into 3 new rewritten queries that more clearly reflect the intent of the original query. The sample demonstrates how to combine the rewritten query results using a manual RRF calculation, an automatic RRF calculation, and how to add semantic ranking to the automatic RRF calculation.

## Prerequisites

- An Azure subscription, with [access to Azure OpenAI](https://aka.ms/oai/access). This sample uses two models:

  - A deployment of the `text-embedding-ada-002` embedding model. As a naming convention, we name deployments after the model name: "text-embedding-ada-002".
  
  - A deployment of a chat model, such as GPT-35-turbo or GPT-4. This example uses JSON mode to return a valid JSON object, which requires a specific version of chat model.
  
    - [Review supported models](https://learn.microsoft.com/azure/ai-services/openai/how-to/json-mode?tabs=python#supported-models) for chat models supporting JSON mode. Note the model version number.
  
    - [Check regional availability](https://learn.microsoft.com/azure/ai-services/openai/concepts/models#standard-deployment-model-availability) of the model you want to use. You might need to switch to an Azure OpenAI resource in a region that supports the model, or you might need to choose a different mode.
  
  - Specify [2023-12-01-preview REST API](https://learn.microsoft.com/azure/ai-services/openai/reference) or later when providing an Azure OpenAI endpoint.

- Azure AI Search, any tier and region, but you must have Basic or higher to try the semantic ranker. This example creates an index. Check your index quota to make sure you have room.

- Python (these instructions were tested with version 3.11.x)

We used Visual Studio Code with the [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) and [Jupyter extension](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter) to test this sample.

## Set up your envrionment variables

The demo-python folder contains a `.env-sample` file that you can modify for your endpoints, keys, and model names.

Remember to omit API keys if you're using Azure role-based permissions. On Azure AI Search, you should have Search Service Contributor, Search Index Data Contributor, and Search Index Data Reader permissions. On Azure OpenAI, you should have Cognitive Services Contributor permissions.

For this notebook, provide the following variables:

```
AZURE_SEARCH_SERVICE_ENDPOINT=<PLACEHOLDER FOR YOUR SEARCH SERVICE ENDPOINT>
AZURE_SEARCH_INDEX=<PLACEHOLDER FOR AN INDEX NAME>
# Optional, do not provide if using RBAC authentication
AZURE_SEARCH_ADMIN_KEY=

AZURE_OPENAI_ENDPOINT=<PLACEHOLDER FOR YOUR AZURE OPEAN ENDPOINT>
# Optional, do not provide if using RBAC authentication and Cognitive Search
AZURE_OPENAI_KEY=
# 2023-12-01-preview and later is required for JSON mode.
AZURE_OPENAI_API_VERSION=2023-12-01-preview

# Use any embedding model on Azure OpenAI
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
# Use any chat model on Azure OpenAI. Remember to check model version and regional availability.
AZURE_OPENAI_CHATGPT_DEPLOYMENT=gpt-35-turbo
```

Save the `.env` file to the `demo-python/code` folder.

## Run the code

1. Open the `code` folder and sample subfolder. Open a `ipynb` file in Visual Studio Code.

1. Optionally, create a virtual environment so that you can control which package versions are used. Use Ctrl+shift+P to open a command palette. Search for `Python: Create environment`. Select `Venv` to create an environment within the current workspace.

1. Execute the cells one by one, or select **Run** or Shift+Enter.

## Troubleshoot errors

If you get error 429 from Azure OpenAI, it means the resource is over capacity:

- Check the Activity Log of the Azure OpenAI service to see what else might be running.

- Check the Tokens Per Minute (TPM) on the deployed model. On a system that isn't running other jobs, a TPM of 33K or higher should be sufficient to generate vectors for the sample data. You can try a model with more capacity if 429 errors persist.

- Review these articles for information on rate limits: [Understanding rate limits](https://learn.microsoft.com/azure/ai-services/openai/how-to/quota?tabs=rest#understanding-rate-limits) and [A Guide to Azure OpenAI Service's Rate Limits and Monitoring](https://clemenssiebler.com/posts/understanding-azure-openai-rate-limits-monitoring/).
