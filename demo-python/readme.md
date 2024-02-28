# Vector search in Python (Azure AI Search)

This repository contains multiple notebooks that demonstrate how to use Azure AI Search for vector and non-vector content in RAG patterns and in traditional search solutions.

Start with [**azure-search-vector-python-sample.ipynb**](code/vectors/azure-search-vector-python-sample.ipynb) for the basic steps. The code reads the `data/text-sample.json` file, which contains the input strings for which embeddings are generated. Output is a combination of human-readable text and embeddings that's pushed into a search index.

![Python Vector Video](https://github.com/Azure/azure-search-vector-samples/blob/main/demo-python/data/images/python-vector-video.gif?raw=true)

Once you understand the basics, continue with the following notebooks for more exploration:

| Sample | Description |
|--------|-------------|
| [azure-search-backup-and-restore.ipynb](./code/index-backup-and-restore/azure-search-backup-and-restore.ipynb) | Backup retrievable index fields and restore it on a different search service. |
| [azure-search-custom-vectorization-sample.ipynb](./code/custom-embeddings/azure-search-custom-vectorization-sample.ipynb) | Integrated data chunking and vectorization using custom skills and open source models. |
| [azure-search-integrated-vectorization-sample.ipynb](./code/integrated-vectorization/azure-search-integrated-vectorization-sample.ipynb) | Integrated data chunking and vectorization (preview) using a skills to split text and call an Azure OpenAI embedding model. |
| [azure-search-vector-image-index-creation-python-sample.ipynb](./code/azure-search-vector-image-index-creation-python-sample.ipynb) | Vectorization using Azure AI Vision image embedding. |
| [azure-search-vector-image-python-sample.ipynb](./code/azure-search-vector-image-python-sample.ipynb)  | Vectorize images using Azure AI Vision image retrieval. |
| [azure-search-vector-python-huggingface-model-sample.ipynb](./code/azure-search-vector-python-huggingface-model-sample.ipynb)  | Vectorize using Hugging Face E5-small-V2 embedding model. |
| [azure-search-vector-python-langchain-sample.ipynb](./code/langchain/azure-search-vector-python-langchain-sample.ipynb) | LangChain integration. |
| [azure-search-vector-python-llamaindex-sample.ipynb](./code/azure-search-vector-python-llamaindex-sample.ipynb) | LlamaIndex integration. |
| [azure-search-vector-python-sample.ipynb](./code/azure-search-vector-python-sample.ipynb) | Basic vector indexing and queries. **Start here**. |

## Prerequisites

To run the Python samples in this folder, you will need the following:

- An Azure subscription, with [access to Azure OpenAI](https://aka.ms/oai/access).
- Azure AI Search, any tier, but choose a service that can handle the workload. We recommend Basic or higher.
- A deployment of the `text-embedding-ada-002` embedding model on Azure OpenAI.
- Azure OpenAI connection and model information:
  - Azure OpenAI API key
  - Azure OpenAI embedding model deployment name (we name deployments after the model name: "text-embedding-ada-002")
  - Azure OpenAI REST API version (we recommend `2023-05-15`)
- Python (these instructions were tested with version 3.11.x)

You can use [Visual Studio Code with the Python extension](https://code.visualstudio.com/docs/python/python-tutorial) for these demos.

## Set up your environment

1. Clone this repository.

1. Create a `.env` based on the `code/.env-sample` file. Copy your new .env file to the folder containing your notebook and update the variables.

1. If you're using Visual Studio Code with the [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python), make sure you also have the [Jupyter extension](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter).

## Run the code

1. Open the `code` folder and sample subfolder. Open a `ipynb` file in Visual Studio Code.

1. Optionally, create a virtual environment so that you can control which package versions are used. Use Ctrl+shift+P to open a command palette. Search for `Python: Create environment`. Select `Venv` to create an environment within the current workspace.

1. Copy the `.env` file to the subfolder containing the notebook.

1. Execute the cells one by one, or select **Run** or Shift+Enter.

## Troubleshoot errors

If you get error 429 from Azure OpenAI, it means the resource is over capacity:

- Check the Activity Log of the Azure OpenAI service to see what else might be running.

- Check the Tokens Per Minute (TPM) on the deployed model. On a system that isn't running other jobs, a TPM of 33K or higher should be sufficient to generate vectors for the sample data. You can try a model with more capacity if 429 errors persist.

- Review these articles for information on rate limits: [Understanding rate limits](https://learn.microsoft.com/azure/ai-services/openai/how-to/quota?tabs=rest#understanding-rate-limits) and [A Guide to Azure OpenAI Service's Rate Limits and Monitoring](https://clemenssiebler.com/posts/understanding-azure-openai-rate-limits-monitoring/).
