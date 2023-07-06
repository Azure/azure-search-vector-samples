# Vector search (public preview) - Azure Cognitive Search

**DISCLAIMER**
Preview functionality is provided under [Supplemental Terms of Use](https://azure.microsoft.com/support/legal/preview-supplemental-terms/), without a service level agreement, and isn't recommended for production workloads.

This repository provides code samples for the [vector search (preview)](https://learn.microsoft.com/azure/search/vector-search-overview) in Azure Cognitive Search.

The demos currently use alpha builds of the Azure SDKs. Instructions for downloading an alpha build can be found in the readme files for each sample.

| Sample | Purpose | Description |
| ------ | ------- | ------------|
| [.NET](demo-dotnet/readme.md) | Creates vector representations of images or text | A .NET Console App that calls Azure OpenAI to create vectorized data. We used this console app to create the sample data for the demo index. You can revise your copy of the notebook to test vector search with other data and your own schemas. See the [sample readme](/demo-dotnet/readme.md) for instructions on console app setup. |                                                                                                                     |
| [Python](demo-python/readme.md) | Creates vector representations of images or text | A notebook that calls Azure OpenAI to create vectorized data. We used this notebook to create the sample data for the demo index. You can revise your copy of the notebook to test vector search with other data and your own schemas. See the [sample readme](/demo-python/readme.md) for instructions on notebook setup. |                                                                                                                                  |
| [JavaScript](demo-javascript/readme.md) | Creates vector representations of images or text | A node.js version of the Python sample. See the [sample readme](/demo-javascript/readme.md) for instructions on sample setup. |                                                                                                                       |
| [Postman collection](postman-collection/Vector%20Search%20QuickStart.postman_collection%20v0.2.json)| Create, load, and query a search index that contains text and vector fields. | A collection of REST API calls to an Azure Cognitive Search instance. The requests in this collection include an index schema, sample documents, and sample queries. The collection is documented in [Quickstart: Vector search](https://learn.microsoft.com/azure/search/search-get-started-vectors). Each query demonstrates key scenarios. <p>Use the [Postman app](https://www.postman.com/downloads/) and import the collection.</p> <p>Set collection variables to provide your search service URI and admin key</p> If you're unfamiliar with Postman, see this [Postman/REST quickstart for Cognitive Search](https://learn.microsoft.com/azure/search/search-get-started-rest). |

## Other resources

- [Azure Search OpenAI Demo](https://github.com/Azure-Samples/azure-search-openai-demo/tree/vectors) A sample app for the Retrieval-Augmented Generation pattern running in Azure, using Azure Cognitive Search for retrieval and Azure OpenAI large language models to power ChatGPT-style and Q&A experiences. Use the "vectors" branch to leverage Vector retrieval.
- [Azure Search OpenAI Demo - C#](https://github.com/Azure-Samples/azure-search-openai-demo-csharp/tree/feature/embeddingSearch) A sample app for the Retrieval-Augmented Generation pattern running in Azure, using Azure Cognitive Search for retrieval and Azure OpenAI large language models to power ChatGPT-style and Q&A experiences using C#.
- [Azure OpenAI Embeddings QnA with Azure Search as a Vector Store](https://github.com/ruoccofabrizio/azure-open-ai-embeddings-qna) (github.com) A simple web application for a OpenAI-enabled document search. This repo uses Azure OpenAI Service for creating embeddings vectors from documents. For answering the question of a user, using Azure Cognitive Search for retrieval and Azure OpenAI large language models to power ChatGPT-style and Q&A experiences.
- [ChatGPT Retreival Plugin Azure Search Vector Database](https://github.com/openai/chatgpt-retrieval-plugin/blob/main/README.md#azure-cognitive-search) The ChatGPT Retrieval Plugin lets you easily find personal or work documents by asking questions in natural language. Azure Cognitive Search now supported as an official vector database.
- [Azure Search Vector Search Demo Web App Template](https://github.com/farzad528/azure-search-vector-search-demo) A Vector Search Demo React Web App Template using Azure OpenAI for Text Search and Cognitive Services Florence Vision API for Image Search.
- [Azure Cognitive Search Documentation](https://learn.microsoft.com/azure/search/)
- [Azure OpenAI Service Documentation](https://learn.microsoft.com/azure/cognitive-services/openai/)
- [Cognitive Services Computer Vision Documentation](https://learn.microsoft.com/azure/cognitive-services/computer-vision/)
