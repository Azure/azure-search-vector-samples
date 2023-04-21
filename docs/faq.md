# FAQ for vector search private preview

Questions about vector search are answered here.

## What is vector search? 

Vector search is a technique used in information retrieval to find similar items in a dataset based on their vector representations. Whether you use an indexer to pull documents into the indexing pipeline, or push documents to an index, Azure Cognitive Search can index documents that contain vector fields.

## How does vector search work? 

Vector search works by accepting a query input represented as a vector. The search engine then calculates the similarity of vector fields in the search index, finding items that are similar to a given query. Both the query and matching content must have a vector representation.

## How is vector search implemented in Cognitive Search?

In Cognitive Search, support for vectors is per-field, which means you can combine vector search and keyword search in the same index. The field's data type determines its characteristics. The data type for a vector field is "Edm.Collection(Single)". Cognitive Search can support hybrid scenarios that combine keyword search and vector search in the same request.

## Can I upload a model to use for vectorization?

You can use any model for vectorization, but you can't upload the model to Azure Cognitive Search because there is no integration at that layer. Cognitive Search can't generate embeddings for the content that it indexes, or for the query inputs that it receives from a client app.

## Cognitive Search has features that are named "vector search" and "semantic search". How is vector search related to semantic search?

The features aren't related, in the sense that you can use them independently. 

+ Vector search introduces requirements on the index schema, the substance and structure of documents, and the types of queries.

+ Semantic re-ranker works on results from keyword search. Internally, Cognitive Search uses deep nerual network models from Bing to re-rank an initial result set, increasing the relevance of results that are a closer semantic match to the initial query. Additionally, Semantic search has features such as answers, captions, and highlights.

You can use vector search and semantic search together. Semantic search will work on fields that do not contain vectorized data. The search engine uses Reciprocal Rank Fusion to merge results from both ranking systems.

## Can I add vector search to an existing index?

No. You must create a new index using the 2023-07-01-preview REST API. Your queries must also specify the preview REST API.

## How can I distinguish a vector search index from a non-vector index?

An index that implements vector search will have:

+ A **`vectorSearch`** section specifying the algorithm (currently, just "hnsw").
+ One or more fields of type **`Collection(Edm.Single)`**, with a **"dimensions"** property and an **"algorithmConfiguration"** property.
+ The request will specify the **2023-07-01-preview** API.
+ On an index that's expressed on your search service, populated vector fields will contain numerical text embeddings instead of human readable content.
