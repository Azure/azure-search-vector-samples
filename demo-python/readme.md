# Vector search in Python (Azure AI Search)

This repository contains multiple notebooks that demonstrate how to use Azure AI Search for vector and non-vector content in RAG patterns and in traditional search solutions.

See [**What's new in Azure AI Search**](https://learn.microsoft.com/azure/search/whats-new) for feature announcements by month and version.

<!-- ![Python Vector Video](https://github.com/Azure/azure-search-vector-samples/blob/main/demo-python/data/images/python-vector-video.gif?raw=true) -->

| Sample | Description | Status |
| ------ | ------------|-------------|
| [advanced-workflow](./code/advanced-workflow/query-rewrite.ipynb) | Demonstrates how to rewrite queries for improved relevance. Examples include hybrid queries and a semanticQuery option. | Beta (see the [ChangeLog](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/CHANGELOG.md) for a package version providing this feature) |
| [basic-vector-workflow](./code/basic-vector-workflow/azure-search-vector-python-sample.ipynb) | **Start here**. Basic vector indexing and queries using push model APIs. The code reads the `data/text-sample.json` file, which contains the input strings for which embeddings are generated. Output is a combination of human-readable text and embeddings that's pushed into a search index. | Generally available |
| **New** [community-integration/cohere](./code/community-integration/cohere/azure-search-cohere-embed-v3-sample.ipynb)| Cohere Embed API integration using the [Cohere Embed API](https://docs.cohere.com/docs/embed-api).| Beta (see the [ChangeLog](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/CHANGELOG.md) for a package version providing this feature) |
| [community-integration/hugging-face](./code/community-integration/hugging-face/azure-search-vector-python-huggingface-model-sample.ipynb) | Hugging Face integration using the [E5-small-V2](https://huggingface.co/intfloat/e5-small-v2) embedding model. | Beta (see the [ChangeLog](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/CHANGELOG.md) for a package version providing this feature) |
| [community-integration/langchain](./code/community-integration/langchain/azure-search-vector-python-langchain-sample.ipynb) | LangChain integration using the [Azure AI Search vector store integration module](https://python.langchain.com/docs/integrations/vectorstores/azuresearch). | Beta (see the [ChangeLog](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/CHANGELOG.md) for a package version providing this feature) |
| [community-integration/llamaindex](./code/community-integration/llamaindex/azure-search-vector-python-llamaindex-sample.ipynb) | LlamaIndex integration using the [llama_index.vector_stores.azureaisearch](https://llamahub.ai/l/vector_stores/llama-index-vector-stores-azureaisearch). | Beta (see the [ChangeLog](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/CHANGELOG.md) for a package version providing this feature)  |
| [custom-vectorizer](./code/custom-vectorizer/azure-search-custom-vectorization-sample.ipynb) | Use an open source embedding model such as Hugging Face sentence-transformers [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) to vectorize content and queries. This sample uses azd and bicep to deploy Azure resources for a fully operational solution. It uses a custom skill with a function app that calls an embedding model.| Beta (see the [ChangeLog](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/CHANGELOG.md) for a package version providing this feature) |
| [data-chunking](./code/data-chunking) | Examples used in the in [Chunk documents](https://learn.microsoft.com/azure/search/vector-search-how-to-chunk-documents) article on the documentation web | Beta (see the [ChangeLog](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/CHANGELOG.md) for a package version providing this feature) |
| [index-backup-restore](./code/index-backup-restore/azure-search-backup-and-restore.ipynb) | Backup retrievable index fields and restore them on a new index on a different search service. | Generally available |
| [integrated-vectorization](./code/integrated-vectorization/azure-search-integrated-vectorization-sample.ipynb) | Demonstrates integrated data chunking and vectorization (preview) using skills to split text and call an Azure OpenAI embedding model. | Beta (see the [ChangeLog](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/CHANGELOG.md) for a package version providing this feature) |
| [multimodal](./code/multimodal/azure-search-vector-image-index-creation-python-sample.ipynb) | Use the push API to vectorize images using [Azure AI Vision multimodal embedding](https://learn.microsoft.com/azure/ai-services/computer-vision/how-to/image-retrieval).| Beta (see the [ChangeLog](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/CHANGELOG.md) for a package version providing this feature) |
| **New** [multimodal-ai-vision](./code/multimodal/azure-ai-search-multimodal-build-demo.ipynb) | Use the pull APIs (an indexer) and built-in skills to vectorize images using [Azure AI Vision multimodal embedding](https://learn.microsoft.com/azure/ai-services/computer-vision/how-to/image-retrieval). In contrast with the multimodal-custom-skill example, this notebook uses the push API (no indexers or skillsets) for indexing. It calls the embedding model directly for a pure image vector search.|  Beta (see the [ChangeLog](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/CHANGELOG.md) for a package version providing this feature) |
| [multimodal-custom-skill](./code/multimodal-custom-skill/azure-search-vector-image-python-sample.ipynb) | Use the pull APIs (an indexer) and a custom skill to vectorize images using [Azure AI Vision multimodal embedding](https://learn.microsoft.com/azure/ai-services/computer-vision/how-to/image-retrieval). This end-to-end sample covers all of the steps, from deployment to queries. | Beta (see the [ChangeLog](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/CHANGELOG.md) for a package version providing this feature) |
| **New** [rag-e2e](./code/rag-e2e/azure-ai-search-e2e-build-demo.ipynb)| Use the new OneLake files indexer to eamlessly integrate data from Google Cloud Platform storage and Amazon Web Services (AWS) S3 with Azure AI Search using the latest AI vectorization techniques. | Beta (see the [ChangeLog](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/CHANGELOG.md) for a package version providing this feature) |
| [vector-quantization-and-storage-options](./code/vector-quantization-and-storage/vector-quantization-and-storage.ipynb) | Sample showcasing how to use vector quantization and various other storage options to reduce storage usage by vector fields. | Beta (see the [ChangeLog](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/search/azure-search-documents/CHANGELOG.md) for a package version providing this feature) |

## Prerequisites

To run the Python samples in this folder, you should have:

- An Azure subscription, with [access to Azure OpenAI](https://aka.ms/oai/access) or other third-party models.
- Azure AI Search, any tier, but choose a service that can handle the workload. We recommend Basic or higher.
- Azure OpenAI is used in most samples. A deployment of the `text-embedding-ada-002` is a common requirement.
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
