---
page_type: sample
languages:
  - python
name: Vector search in Python
products:
  - azure
  - azure-cognitive-search
  - azure-openai
description: |
  Using azure-search-documents and the Azure SDK for Python, index and query vectors in a RAG pattern or a traditional search solution.
urlFragment: vector-search-python
---

# Basic vector demo using Python (Azure AI Search)  

The Python notebook creates vectorized data on Azure AI Search and runs a series of queries, returning output to the notebook.

- Create an index schema
- Load the sample data
- Embed the documents in-memory
- Index the vector and nonvector fields
- Run a series of vector and hybrid queries

The sample data is a JSON file of 108 descriptions of various Azure services. The descriptions are short, which makes data chunking unnecessary.

The queries are articulated as strings. An Azure OpenAI embedding model converts the strings to vectors at run time. Queries include a pure vector query, vector with fitlers, hybrid query, hybrid with semantic ranking, and a multivector query.

For further exploration and chat interaction, connect to your index using Azure OpenAI Studio.

## Prerequisites

- An Azure subscription, with [access to Azure OpenAI](https://aka.ms/oai/access).

- Azure AI Search, any version, but make sure search service capacity is sufficient for the workload. We recommend Basic or higher for this demo.

- A deployment of the `text-embedding-3-large` embedding model in your Azure OpenAI service. We recommend Azure OpenAI REST API version `2024-06-01`. As a naming convention, we name deployments after the model name: "text-embedding-3-large". By default, 1024 dimensions are used.

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
