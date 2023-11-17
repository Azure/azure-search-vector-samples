# Vector search (public preview) - Azure AI Search

**DISCLAIMER**
Preview functionality is provided under [Supplemental Terms of Use](https://azure.microsoft.com/support/legal/preview-supplemental-terms/), without a service level agreement, and isn't recommended for production workloads.

This repository provides code samples for the [vector search (preview)](https://learn.microsoft.com/azure/search/vector-search-overview) in Azure AI Search.

The demos currently use beta versions of the client libraries for the Azure SDKs.

| Sample | Description |
| ------ | ------------|
| [.NET](demo-dotnet/readme.md) | A .NET Console App that calls Azure OpenAI to create vectorized data. It then calls Azure AI Search to create, load, and query the data.|
| [Python](demo-python/readme.md) |  A series of notebooks that demonstrate aspects of vector search, including data chunking and vectorization of both text and image content. |
| [JavaScript](demo-javascript/readme.md) | There are three code samples. One is an end-to-end code sample that calls Azure OpenAI for embeddings and Azure AI Seach to create, load, and query an index that contains vectors. Another sample calls just Azure OpenAI and is used to generate embeddings for fields in an index. The last one also calls just Azure OpenAI and is used to generate an embedding for a vector query.  |
| [Postman collection](postman-collection/Vector%20Search%20QuickStart.postman_collection%20v1.0.json)| A collection of REST API calls to an Azure AI Search instance to create, load, and query a search index that contains text and vector fields. The requests in this collection include an index schema, sample documents, and sample queries. The collection is reference in [Quickstart: Vector search](/docs/vector-search-quickstart.md). Each query demonstrates key scenarios. <p>Use the [Postman app](https://www.postman.com/downloads/) and import the collection.</p> <p>Set collection variables to provide your search service URI and admin key</p> If you're unfamiliar with Postman, see this [Postman/REST quickstart for AI Search](https://learn.microsoft.com/azure/search/search-get-started-rest). |

## Related resources

- [Azure Search OpenAI Demo](https://github.com/Azure-Samples/azure-search-openai-demo/tree/vectors) A sample app for the Retrieval-Augmented Generation pattern running in Azure, using Azure AI Search for retrieval and Azure OpenAI large language models to power ChatGPT-style and Q&A experiences. Use the "vectors" branch to leverage Vector retrieval.
- [Azure Search OpenAI Demo - C#](https://github.com/Azure-Samples/azure-search-openai-demo-csharp/tree/feature/embeddingSearch) A sample app for the Retrieval-Augmented Generation pattern running in Azure, using Azure AI Search for retrieval and Azure OpenAI large language models to power ChatGPT-style and Q&A experiences using C#.
- [Azure OpenAI Embeddings QnA with Azure Search as a Vector Store](https://github.com/ruoccofabrizio/azure-open-ai-embeddings-qna) (github.com) A simple web application for a OpenAI-enabled document search. This repo uses Azure OpenAI Service for creating embeddings vectors from documents. For answering the question of a user, using Azure AI Search for retrieval and Azure OpenAI large language models to power ChatGPT-style and Q&A experiences.
- [ChatGPT Retreival Plugin Azure Search Vector Database](https://github.com/openai/chatgpt-retrieval-plugin/blob/main/README.md#azure-cognitive-search) The ChatGPT Retrieval Plugin lets you easily find personal or work documents by asking questions in natural language. Azure AI Search now supported as an official vector database.
- [Azure Search Vector Search Demo Web App Template](https://github.com/farzad528/azure-search-vector-search-demo) A Vector Search Demo React Web App Template using Azure OpenAI for Text Search and Cognitive Services Florence Vision API for Image Search.
- [Azure AI Search Documentation](https://learn.microsoft.com/azure/search/)
- [Azure OpenAI Service Documentation](https://learn.microsoft.com/azure/cognitive-services/openai/)
- [Azure AI Search Comparision Tool](https://github.com/Azure-Samples/azure-search-comparison-tool)
- [Azure AI Vision Documentation](https://learn.microsoft.com/azure/cognitive-services/computer-vision/)
