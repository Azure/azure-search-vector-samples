# FAQ for vector search private preview

Questions about vector search are answered here.

## What is vector search? 

Vector search is a technique used in information retrieval to find similar items in a dataset based on their vector representations. 

## How does vector search work? 

Vector search works by accepting a query input represented as a vector. The search engine then calculates the similarity of vector fields in the search index, finding items that are similar to the given vector query. Because it's too expensive to compare the query vector to all vectors in the index, vector search uses Approximate Nearest Neighbor (ANN) algorithms to find the nearest match. This improves query speed, at the cost of recall.

## How vector search works in Cognitive Search?

In Cognitive Search, you can index vector data as fields in documents alongside textual and other [types of content](https://learn.microsoft.com/en-us/rest/api/searchservice/supported-data-types). The data type for a vector field is "Collection(Edm.Single)", but other types of vector fields will be supported in the future, like Collection(Edm.Double) and Collection(Edm.Int32). Vector fields can be populated using an [Indexer](https://learn.microsoft.com/en-us/azure/search/search-indexer-overview) or by the [Push API](https://learn.microsoft.com/en-us/azure/search/search-what-is-data-import#pushing-data-to-an-index).

Vector queries can be issued standalone or in combination with other query types including term queries and filters in the same search request.

## Can Cognitive Search vectorize my content or queries?

Today Cognitive Search doesn't perform vectorization. It's up to the application layer to pick the best model for the data and generate embeddings for the content that it indexes and for the queries.

## Cognitive Search has features that are named "vector search" and "semantic search". How is vector search related to semantic search?

The features aren't related, in the sense that you can use them independently. 

+ Vector search adds vectors as a new type of data and allows you to store and retrieve them efficiently. This opens a whole new set of scenarios that Cognitive Search can enable including multi-modal content retrieval, vector store for applications using Large Language Models (LLMs), recommendation systems, hybrid search scenarios, and more.

+ Semantic search works on the results retrieved by the search engine. Cognitive Search uses deep neural network models from Bing to re-rank to results retrieved by the search engine, increasing the relevance of results that are a closer semantic match to the query. Additionally, Semantic search has features such as answers, captions, and highlights. 

You can use vector search and semantic search together if the search request contains a text query - hybrid search. The search engine uses Reciprocal Rank Fusion to merge results from both vector and term queries before semantic search reranking is applied.

## Can I add vector search to an existing index?

No. You must create a new index using the 2023-07-01-preview REST API. Your queries must also specify the preview REST API.

## How to enable vector search on a search index?

To enable vector search in an index you will need:

+ Add one or more fields of type **`Collection(Edm.Single)`**, with a **"dimensions"** property and an **"algorithmConfiguration"** property.
+ Add **`vectorSearch`** section to the index definition specifying the configuraiton used by vector search fields, including the parameters of the Approximate Nearest Neighbor algorithm used, like HNSW.
+ Use the **2023-07-01-Preview** API verison.
+ Index documents with vector content using an [Indexer](https://learn.microsoft.com/en-us/azure/search/search-indexer-overview) or the [Push API](https://learn.microsoft.com/en-us/azure/search/search-what-is-data-import#pushing-data-to-an-index).
