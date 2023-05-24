# General guidelines for data chunking to generate embedding vectors

When using Natural Language Processing (NLP), the REST APIs that generate embedding vectors for text fragments have text input limits. For example, the maximum length of input text for the [Azure OpenAI](https://learn.microsoft.com/azure/cognitive-services/openai/how-to/embeddings) embedding models is 2048 tokens (equivalent to around 2-3 pages of text). If you're using these models to generate embeddings, it's critical that the input text stays under the limit. Partitioning your content into chunks ensures that your data can be processed by the Large Language Models (LLM) used for indexing and queries.

## Factors to consider when chunking data

When it comes to chunking data, think about these factors:

1. Type and size of data: the shape and density of your documents will determine the best approach to chunking.

2. User queries: understanding the types of queries your users make will enable you to create chunks that contain the necessary data to respond to their queries.

3. Chunk content overlap: you need overlap between chunks so that the semantics are not lost in the transition between chunks.

4. Large Language Models (LLM) have performance guidelines for chunk size, and you'll need to set a chunk size that works best for all of the models you're using. For instance, if you use models for summarization and embeddings, choose an optimal chunk size that works for both.

@GIA - I don't understand how #2 user queries is a factor chunking?  Can you help connect the dots?

## Common chunking techniques

Here are some common chunking techniques, starting with the most widely used method:

1. Fixed-size chunks: Define a fixed size that's sufficient for semantically meaningful paragraphs (for example, 200 words) and allows for some overlap (for example, 10-15% of the content) can produce good chunks as input for embedding vector generators.

1. Variable-sized chunks based on content: Partition your data based on content characteristics, such as end-of-sentence punctuation marks, end-of-line markers, or using features in the Natural Language Processing (NLP) libraries. Markdown language structure can also be used to split the data.

1. Combine chunking techniques: You can mix techniques for different scenarios. For example, when dealing with large documents, creating text chunks that append the document title with data located in the middle of the document could help prevent context loss.

@GIA - for combo chunking, we definitely need a link because in the previous section, the implication is one chunk size for all, but then in this section, we say you can mix it up....

## Content overlap considerations

When chunking data, overlapping a small amount of text between chunks can help preserve context. We recommend starting with an overlap of approximately 10%. For example, given a fixed chunk size of 256 tokens, you would begin testing with an overlap of 25 tokens. The actual amount of overlap varies depending on the type of data and the specific use case, but we have found that 10-15% works for many scenarios.

## Simple approach of how to create chunks with sentences

This section demonstrates the logic of creating chunks out of sentences. For this example, assume the following:

+ Tokens are equal to words.
+ Input = `text_to_chunk(string)`
+ Output = `sentences(list[string])`

### Sample input

"Barcelona is a city in Spain. It is close to the sea and /n the mountains /n You can both ski in winter and swim in summer."

+ Sentence 1 contains 6 words: "Barcelona is a city in Spain."
+ Sentence 2 contains 9 words: "It is close to the sea and /n the mountains."
+ Sentence 3 contains 10 words: "You can both ski in winter and swim in summer."

@GIA - what is the significance of /n, how does /n relate to chuncking, and what's happenedd to /n in the examples because they seem to be dropping off.

### Approach 1: Sentence chunking with "no overlap"

Given a maximum number of tokens, iterate through the sentences and concatenate sentences until the maximum token length is reached. If a sentence is bigger than the maximum number of chunks, truncate to a maximimum amount of tokens, and put the rest in the next chunk.

**Example: maximum tokens = 10**

```
Barcelona is a city in Spain.
It is close to the sea and the mountains.
You can both ski in winter and swim in summer.
```

**Example: maximum tokens = 16**

```
Barcelona is a city in Spain. It is close to the sea and the mountain. 
You can both ski in winter and swim in summer.
```
    
**Example: maximum tokens = 6**

@GIA - who or what is adding the periods after every 6 tokens??

```
Barcelona is a city in Spain.
It is close to the sea. 
and the mountains. 
You can both ski in winter.
and swim in summer.
```

### Approach 2: Sentence chunking with "10% overlap"

Follow the same logic with no overlap approach, except that you create an overlap between chunks according to certain ratio.
A 10% overlap on maximum tokens of 10 is one token.

@GIA - is this example correct? 

**Example: maximum tokens = 10**

```
Barcelona is a city in Spain. It
It is close to the sea and the mountains. You
You can both ski in winter and swim in summer.
```

## Learn more about embedding models in Azure OpenAI

+ [Understanding embeddings in Azure OpenAI Service](https://learn.microsoft.com/azure/cognitive-services/openai/concepts/understand-embeddings)
+ [Learn how to generate embeddings](https://learn.microsoft.com/azure/cognitive-services/openai/how-to/embeddings?tabs=console)
+ [Tutorial: Explore Azure OpenAI Service embeddings and document search](https://learn.microsoft.com/azure/cognitive-services/openai/tutorials/embeddings?tabs=command-line)
