---
page_type: sample
languages:
  - python
name: Query Rewriting in Python
products:
  - azure
  - azure-cognitive-search
  - azure-openai
description: |
  Using azure-search-documents and the Azure SDK for Python, demonstrate how to use query rewriting to improve your search relevance with hybrid search and Reciprocal Rank Fusion
urlFragment: vector-search-python
---

# Query Rewriting using Python (Azure AI Search)  

The Python notebook creates vectorized data on Azure AI Search and demonstrates how a query rewriting technique can be used to search it, returning output to the notebook.

- Create an index schema
- Load the sample data
- Embed the documents in-memory
- Index the vector and nonvector fields
- Run a hybrid search
- Rewrite the hybrid search query for improved relevance
- Combine multiple rewritten queries using a manual Reciprocal Rank Fusion (RRF) calculation.
- Combine multiple rewritten queries using an automatic RRRF calculation
- Use semantic ranking to ruther improve relevance.

The sample data is a JSON file of 108 descriptions of various Azure services. The descriptions are short, which makes data chunking unnecessary.

The queries are articulated as strings. An Azure OpenAI embedding model converts the strings to vectors at run time. The text query and the vector query are combined at run time to produce a hybrid query.

The sample includes a simple prompt that is used to rewrite the queries into 3 new rewritten queries that more clearly reflect the intent of the original query. The sample demonstrates how to combine the rewritten query results using a manual RRF calculation, an automatic RRF calculation, and how to add semantic ranking to the automatic RRF calculation.

## Prerequisites

- An Azure subscription, with [access to Azure OpenAI](https://aka.ms/oai/access).

- Azure AI Search, any version, but make sure search service capacity is sufficient for the workload. We recommend Basic or higher for this demo.

- A deployment of the `text-embedding-ada-002` embedding model in your Azure OpenAI service. We recommend Azure OpenAI REST API version `2023-05-15`. As a naming convention, we name deployments after the model name: "text-embedding-ada-002".

- Python (these instructions were tested with version 3.11.x)

We used Visual Studio Code with the [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) and [Jupyter extension](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter) to test this sample.

## Run the code

1. Use the `code/.env-sample` as a template for a new `.env` file located in the subfolder containing the notebook. Review the variables to make sure you have values for Azure AI Search and Azure OpenAI.

1. Open the `code` folder and sample subfolder. Open a `ipynb` file in Visual Studio Code.

1. Optionally, create a virtual environment so that you can control which package versions are used. Use Ctrl+shift+P to open a command palette. Search for `Python: Create environment`. Select `Venv` to create an environment within the current workspace.

1. Execute the cells one by one, or select **Run** or Shift+Enter.

## Troubleshoot errors

If you get error 429 from Azure OpenAI, it means the resource is over capacity:

- Check the Activity Log of the Azure OpenAI service to see what else might be running.

- Check the Tokens Per Minute (TPM) on the deployed model. On a system that isn't running other jobs, a TPM of 33K or higher should be sufficient to generate vectors for the sample data. You can try a model with more capacity if 429 errors persist.

- Review these articles for information on rate limits: [Understanding rate limits](https://learn.microsoft.com/azure/ai-services/openai/how-to/quota?tabs=rest#understanding-rate-limits) and [A Guide to Azure OpenAI Service's Rate Limits and Monitoring](https://clemenssiebler.com/posts/understanding-azure-openai-rate-limits-monitoring/).
