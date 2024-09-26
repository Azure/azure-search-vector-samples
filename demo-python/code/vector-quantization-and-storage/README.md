---
page_type: sample
languages:
  - python
name: Vector quantization and storage options in Python
products:
  - azure
  - azure-ai-search
description: |
  Using azure-search-documents and the Azure SDK for Python, save on storage when using vector quantization.
urlFragment: quantization-storage-python
---

# Vector quantization and storage options using Python (Azure AI Search)  

The Python notebook creates vectorized data on Azure AI Search and demonstrates how to save on storage using the following features

- Built-in scalar quantization that reduces vector index size in memory and on disk.
- Disabling storage of vectors returned in query responses. These vectors are stored separately from vectors used for the queries themselves.
- Smaller data types than `Edm.Single`.
- Truncating dimensions of vectors.

The sample data is a JSON file containing a pre-chunked version of the sample documents about a fictious company called Contoso Electronics and their policies. They have been embedded using text-embedding-3-large with 3072 dimensions.

## Prerequisites

- An Azure subscription, with [access to Azure OpenAI](https://aka.ms/oai/access).

- Azure AI Search, any version, but make sure search service capacity is sufficient for the workload. We recommend Basic or higher for this demo.

- Python (these instructions were tested with version 3.11.x)

We used Visual Studio Code with the [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) and [Jupyter extension](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter) to test this sample.

## Run the code

1. Use the `code/.env-sample` as a template for a new `.env` file located in the subfolder containing the notebook. Review the variables to make sure you have values for Azure AI Search and Azure OpenAI.

1. Open the `code` folder and sample subfolder. Open a `ipynb` file in Visual Studio Code.

1. Optionally, create a virtual environment so that you can control which package versions are used. Use Ctrl+shift+P to open a command palette. Search for `Python: Create environment`. Select `Venv` to create an environment within the current workspace.

1. Execute the cells one by one, or select **Run** or Shift+Enter.
