# How to create and use embeddings for search queries and documents

Cognitive Search doesn't host machine learning algorithms for vector search, so one of your challenges is creating embeddings for query inputs and outputs. You can use any machine learning algorithm that generates embeddings, but this article assumes the Azure OpenAI. Demos in the private preview tap the [similarity embedding models](https://learn.microsoft.com/azure/cognitive-services/openai/concepts/models#embeddings-models) of Azure OpenAI.

## How models are used

+ Query inputs will require that you submits user-provided input to a machine learning algorithm that quickly converts human readable text into a vector. Optimizing for speed is the objective. Choosing a fast algorithm, co-located with Cognitive Search in the same region, helps you reduce latency. 

  + We used **text-embedding-ada-002** to generate embeddings.
  
  + To increase the success rate of generation, we slowed the rate at which calls to the model are made. For the Python demo, we used [tenacity](https://pypi.org/project/tenacity/).

+ Query outputs will be any matching documents found in a search index. Your search index must have been previously loaded with documents having one or more vector fields with embeddings. Whatever model you used for indexing, use the same model for queries.

## Co-locate resources in the same region

If you want resources in the same region, start with:

1. [A region for the similarity embedding model](https://learn.microsoft.com/azure/cognitive-services/openai/concepts/models#embeddings-models-1), currently in Europe and the United States.

1. [A region for Cognitive Search](https://azure.microsoft.com/explore/global-infrastructure/products-by-region/?products=cognitive-search). 

1. To support hybrid queries that include [semantic ranking](https://learn.microsoft.com/azure/search/semantic-how-to-query-request?tabs=portal%2Cportal-query), or if you want to try machine learning model integration using a [custom skill](https://learn.microsoft.com/azure/search/cognitive-search-custom-skill-interface) in an [AI enrichment pipeline](https://learn.microsoft.com/azure/search/cognitive-search-concept-intro), note the regions that provide those features.

## Generate an embedding for an ad hoc query

The Postman collection assumes that you already have a vector query. Here's some Python code for generating an embedding that you can paste into the "values" property of a vector query.

```python
! pip install openai

import openai

openai.api_type = "azure"
openai.api_key = "YOUR-API-KEY"
openai.api_base = "https://YOUR-OPENAI-RESOURCE.openai.azure.com"
openai.api_version = "2022-12-01"

response = openai.Embedding.create(
    input="How do I use Python in VSCode?",
    engine="text-embedding-ada-002"
)
embeddings = response['data'][0]['embedding']
print(embeddings)
```

## Tips and recommendations for embedding model integration

+ Python and JavaScript demos offer more scalability than the REST APIs for generating embeddings. As of this writing, the REST API doesn't currently support batching.

+ We've done proof-of-concept testing with indexers and skillsets, where a custom skill calls a machine learning model to generate embeddings. There is currently no tutorial or walkthrough, but we intend to provide this content as part of the public preview launch, if not sooner.

+ We've done proof-of-concept testing of embeddings for a thousand images using [image retrieval vectorization in Cognitive Services](https://learn.microsoft.com/azure/cognitive-services/computer-vision/how-to/image-retrieval). We hope to provide a demo of this soon.

+ Similarity search expands your options for searchable content, for example by matching image content with text content, or matching across multiple languages. But not every query is improved with vector search. Keyword matching with BM25 is cheaper, faster, and easier, so integrate vector search only where it adds value.

## Learn more about embedding models in Azure OpenAI

+ [Understanding embeddings in Azure OpenAI Service](https://learn.microsoft.com/azure/cognitive-services/openai/concepts/understand-embeddings)
+ [Learn how to generate embeddings](https://learn.microsoft.com/azure/cognitive-services/openai/how-to/embeddings?tabs=console)
+ [Tutorial: Explore Azure OpenAI Service embeddings and document search](https://learn.microsoft.com/azure/cognitive-services/openai/tutorials/embeddings?tabs=command-line)
