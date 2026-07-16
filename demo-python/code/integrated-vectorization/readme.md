---
page_type: sample
languages:
  - python
name: Integrated vectorization (Python)
products:
  - azure
  - azure-cognitive-search
  - azure-openai
description: |
  Using azure-search-documents and the Azure SDK for Python, apply data chunking and vectorization in an indexer pipeline.
urlFragment: integrated-vectors-python
---

# Integrated vectorization using Python (Azure AI Search)  

The Python notebook creates vectorized data on Azure AI Search and runs a series of queries.

The code reads the `data/text-sample.json` file, which contains the input strings for which embeddings are generated. Output is a combination of human-readable text and embeddings that are pushed into a search index.

## Prerequisites

- An Azure subscription, with [access to Azure OpenAI](https://aka.ms/oai/access).

- Azure AI Search, any version, but make sure search service capacity is sufficient for the workload. We recommend Basic or higher for this demo.

- Azure AI Search data-plane access that matches the notebook credential:
  - If you set `AZURE_SEARCH_ADMIN_KEY`, go to **Settings > Keys** on the search service and select **API Keys** or **Both**.
  - If you don't set `AZURE_SEARCH_ADMIN_KEY`, select **Role-based access control** or **Both**. Assign your signed-in identity **Search Service Contributor** to create search objects and **Search Index Data Reader** (or the broader **Search Index Data Contributor**) to run queries.

- Azure Storage, with a blob container containing documents to load, chunk, and vectorize. Depending on which integrated vectorization options you choose, different sample data is provided

- A deployment of the `text-embedding-3-large` or `text-embedding-3-small` embedding model in your Azure OpenAI service. We recommend Azure OpenAI REST API version `2024-10-21`. As a naming convention, we name deployments after the model name: "text-embedding-3-large".

- Azure OpenAI access for the search service. Choose one authentication mode:
  - For key-based authentication, set `AZURE_OPENAI_KEY` to a key from the Azure OpenAI resource and leave `AZURE_OPENAI_USE_MANAGED_IDENTITY` set to `false`.
  - For managed identity, leave `AZURE_OPENAI_KEY` empty, set `AZURE_OPENAI_USE_MANAGED_IDENTITY` to `true`, enable a system-assigned managed identity on the Azure AI Search service, and assign that identity **Cognitive Services OpenAI User** on the Azure OpenAI resource. Assigning this role to the notebook user does not authorize the search service.

- Python (these instructions were tested with version 3.11.x)

We used Visual Studio Code with the [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) and [Jupyter extension](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter) to test this sample.

## Run the code

1. Use the `code/.env-sample` as a template for a new `.env` file located in the subfolder containing the notebook. Review the variables to make sure you have values for Azure AI Search and Azure OpenAI.

1. The Document Intelligence layout skill is only available in the regions listed here: https://learn.microsoft.com/azure/search/cognitive-search-skill-document-intelligence-layout

1. Open `demo-python/code/integrated-vectorization/azure-search-integrated-vectorization-sample.ipynb` file in Visual Studio Code.

1. Optionally, create a virtual environment so that you can control which package versions are used. Use Ctrl+shift+P to open a command palette. Search for `Python: Create environment`. Select `Venv` to create an environment within the current workspace.

1. Execute the cells one by one, or select **Run** or Shift+Enter.

1. After the indexer finishes, run the notebook's search access and content preflight. Don't continue to the query cells until it reports at least one indexed document.

## Troubleshoot errors

If the notebook preflight or **Search Explorer** can't query the index, verify the search service's **Settings > Keys** selection matches the credential mode described in the prerequisites. For role-based access, also verify that your portal identity has **Search Index Data Reader** or **Search Index Data Contributor**. If access succeeds but the document count is zero, wait for the indexer to complete and review its execution history for errors.

If a vector query returns **The vectorization endpoint returned status code '401'**, Azure AI Search couldn't authenticate to Azure OpenAI. Verify the authentication mode described in the prerequisites. For key-based authentication, confirm `AZURE_OPENAI_KEY` belongs to the resource named by `AZURE_OPENAI_ENDPOINT`. For managed identity, confirm the search service's identity has **Cognitive Services OpenAI User** on that Azure OpenAI resource. After correcting authentication, rerun the cells that create the index and skillset so their stored vectorizer and embedding-skill configuration is updated.

If you get error 429 from Azure OpenAI, it means the resource is over capacity:

- Check the Activity Log of the Azure OpenAI service to see what else might be running.

- Check the Tokens Per Minute (TPM) on the deployed model. On a system that isn't running other jobs, a TPM of 33K or higher should be sufficient to generate vectors for the sample data. You can try a model with more capacity if 429 errors persist.

- Review these articles for information on rate limits: [Understanding rate limits](https://learn.microsoft.com/azure/ai-services/openai/how-to/quota?tabs=rest#understanding-rate-limits) and [A Guide to Azure OpenAI Service's Rate Limits and Monitoring](https://clemenssiebler.com/posts/understanding-azure-openai-rate-limits-monitoring/).
