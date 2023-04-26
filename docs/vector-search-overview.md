# Vector search in Azure Cognitive Search

Vector search uses numerics instead of keywords to formulate queries and find matching documents. It's based on scans over a vector space, populated with embeddings that can describe the content of an item as a vector. Instead of ASCII matching on keywords or phrases, vector search looks for matches that have a similar composition. 

 <!-- copied from azure OpenAI docs -->
As explained in [this Azure OpenAI article](https://learn.microsoft.com/azure/cognitive-services/openai/concepts/understand-embeddings), each embedding is a vector of floating-point numbers, such that the distance between two embeddings in the vector space is correlated with semantic similarity between two inputs in the original format. For example, if two texts are similar, then their vector representations should also be similar.

By performing similarity searches over vector representations of your data, you can find information that's similar to your search query, even if the search terms don't match up perfectly to the indexed content. While in some cases direct comparisons are appropriate (for example, find exact words in a sentence), a similarity search can help you find items that are semantically aligned, regardless of their representation or media type.

> [!NOTE]
> Vector search is term-agnostic, so it's possible to get results from a corpus that doesn't include the terms that you've generated embeddings for. For example, if you generate an embedding for "best pets for small children" and submit it to a corpus containing recipes, you might get a match even if the corpus doesn't contain most of those terms.

## Terms and concepts

*Vectorization* converts chunks of text and other content to a mathematical representation.

*Vector fields* are of type "Collection(Edm.Single)" and are populated with embeddings (floating point numbers, which can be thousands depending on the size and complexity of the input).

*Embedding* refers to a single vector representation of an object. It's a mathematical representation of an object, such as a word, sentence, or document, in a continuous vector space. This numerical representation allows for comparisons and analysis of the relationships between objects. In natural language processing (NLP) and machine learning, embeddings are often used to convert text data into numerical data that can be easily processed by algorithms. 

*Embeddings* are a specific type of vector representation created by machine learning models that capture the semantic meaning of words or other content. For text, machine learning algorithms analyze large amounts of data to identify patterns and relationships between words. The resulting embeddings are high-dimensional vectors, where words with similar meanings are closer together in the vector space.

## What can you do with vectors in Cognitive Search?

You can create embeddings for documents, sentences, images, or audio. Embeddings might be trained on a single type of data (such as sentence embeddings), while others map multiple types of data into the same vector space (for example, sentences and images).

In Azure Cognitive Search, vector search is integrated with the rest of the system. A [search index](https://learn.microsoft.com/azure/search/search-what-is-an-index) can have vector fields combined with text fields used for keyword search.

+ **Vector search for text**. You can encode text input using embedding models such as OpenAI embeddings or open source software (OSS) models such as SBERT, and retrieve with queries that are also encoded as vectors. 1. 

+ **Vector search across different data types**. You can encode images, text, audio, and video, or even a mix of them (for example, with models like CLIP) and do a similarity search across them.

+ **Multi-lingual search**: Because searchable content is represented mathematically, a vector search can resolve to semantically similar content in multiple languages. 

+ **Hybrid search**. For text data, you can combine the best of vector retrieval and keyword retrieval to obtain the best results. Use with semantic search (preview) for even more accuracy with L2 reranking using the same language models that power Bing.  

  Internally, within a single search index, there are inverted indexes for keyword search over text fields, and vector indexes for vector search. In hybrid scenarios, both forms of search are performed and the results are unified before the response is sent back.

+ **Vector store**. A common scenario is to vectorize all of your data into a vector database, and then when the application needs to find an item, you use a query vector to retrieve similar items. Because Cognitive Search can store vectors, you could use it purely as a vector store.

## Reciprocal Rank Fusion

For hybrid search scoring, we use Reciprocal Rank Fusion. Reciprocal Rank Fusion (RRF) is a technique used in information retrieval, specifically for combining the results of different search systems to produce a single, more accurate and relevant result. It is based on the concept of reciprocal rank, which is the inverse of the rank of the first relevant document in a list of search results. 

At a basic level, RRF works by taking the search results from multiple systems, assigning a reciprocal rank score to each document in the results, and then combining these scores to create a new ranking. The main idea behind this method is that documents appearing in the top positions across multiple search systems are likely to be more relevant and should be ranked higher in the combined result. 

Here's a simple explanation of the RRF process: 

1. Obtain search results from multiple systems: Let's say we have two search systems, A and B. We search for a specific query on both systems and get ranked lists of documents as results. 

2. Assign reciprocal rank scores: For each document in the search results, we assign a reciprocal rank score based on its position in the list. The score is calculated as 1/(rank + k), where rank is the position of the document in the list, and k is a constant, usually set to a small value like 60.

3. Combine scores: For each document, we sum the reciprocal rank scores obtained from each search system. This gives us a combined score for each document. 

4. Rank documents based on combined scores: Finally, we sort the documents based on their combined scores, and the resulting list is the fused ranking.



## Next steps

+ [Try the quickstart](vector-search-quickstart.md) to learn the REST APIs and field definitions used in vector search
+ [Try the Python](../demo-python/) or [JavaScript](../demo-javascript/) demos to generate embeddings from Azure OpenAI
+ [Learn more about embeddings](vector-search-how-to.md) and how to use them in Cognitive Search