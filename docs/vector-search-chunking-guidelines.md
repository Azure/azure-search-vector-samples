# General guidelines for data chunking to generate embedding vectors

When using Natural Language Processing (NLP), REST APIs that generate embedding vectors for text fragments, like [Azure OpenAI]( https://learn.microsoft.com/azure/cognitive-services/openai/how-to/embeddings), have a fixed length limit for their input text. It is critical to validate that the input text is within the limit before making a request. Based on this, data needs to be partitioned into smaller pieces and techniques must be used to ensure this is done efficiently for effective search across these pieces. This technique is called chunking, which is the process of dividing data into smaller portions that can be processed by Large Language Models (LLM).

## Factors to consider when chunking data

When it comes to chunking data, various factors need to be considered to have a successful outcome, such as:
1.	Type and size of data: Your data type (such as content, catalogue and such) short documents, or long documents, will determine the best approach to chunking your data.
2.	User queries: Understanding the types of queries your users make will enable you to create chunks that contain the necessary data to respond to their queries.
3.	Chunk content overlap: The amount of overlap between chunks is important to ensure that the semantics are not lost between one chunk and the other. 
4.	Large Language Models (LLM) and their performance guidelines: Your end-to-end pipeline's  performance guidelines regarding chunking sizes should be considered to ensure that you use a chunk size that works best for all of them. In other words, if you use

## Common chunking techniques

Here are some common chunking techniques, starting with the most widely used method:
1.	Fixed-size chunks: This technique involves defining a fixed size for the chunks. A small chunk size that contains semantically meaningful paragraphs (e.g., 200 words) and allows for some overlap (e.g., 10-15% of the content) can produce good chunks as input for embedding vector generators.
1.	Variable-sized chunks based on content: This technique involves chunking the data based on the content, such as by separating into sentences using punctuation marks or end-of-line markers or using Natural Language Processing (NLP) libraries. Markdown language structure can also be used to split the data.
1.	Combining chunking techniques: Different techniques can be mixed or tried for different scenarios. For example, when dealing with large documents, creating text chunks that append the document title with data located in the middle of the document could help prevent context loss.

## Content overlap considerations

When chunking data is generally recommended to start testing with an overlap of approximately 10% and then adjust as needed. A 10-15% overlap is typically sufficient for most cases. For example, if you have a fixed chunk size of 256 tokens, you can begin testing with an overlap of 25 tokens. This will help in some cases prevent the semantics of the text from being lost between chunks. It is important to note that the specific amount of overlap needed may vary depending on the type of data being used and the specific use case. Therefore, it is recommended to experiment with different overlap percentages to find the best approach for your specific scenario.

## Simple approach of how to create chunks with sentences

This section has the logic of a simple approach of creating chunks with sentences. For the sake of this example and to simplify the demonstration of how this works, tokens will be equal to words and this is language agnostic. This is not generally the case when tokenizing sentences. These are the steps and the logic used:
1. Use heuristics to identify individual sentences within a lengthy text phrase, where:
    ```
    Input = text_to_chunk(string)
    Output = sentences(list[string])
    ```
   Text to chunk: 
   ```
   Barcelona is a city in Spain. It is close to the sea and /n the mountain /n You can both ski in winter and swim in summer.
   ```
   How the text is chunked:
   
   - Sentence 1 contains 6 words:
     ```
     Barcelona is a city in Spain.
     ```
   - Sentence 2 contains 9 words:
     ```
     It is close to the sea and /n the mountain
     ```
   - Sentence 3 contains 10 words:
     ```
     You can both ski in winter and swim in summer
     ```
2. Create chunks by concatenating the sentences:

    a) **No overlap approach**:
       
       Input = sentences(list[string])
       Output = chunks(list[string])
       
    Logic:
    - Iterate through sentences and concatenate text until the maximum number of tokens is reached. The last sentence should go in the next chunk.
    - If a sentence is bigger than the maximum number of chunks, truncate to a maximimum amount of tokens and put the rest in the next chunk.

        Example with the text above:
        With maximum tokens = 10, these are the chunks created:
        
        ```
        Barcelona is a city in Spain.
        It is close to the sea and the mountain.
        You can both ski in winter and swim in summer.
        ```
        With maximum tokens = 16, these are the chunks created:
        ```
        Barcelona is a city in Spain. It is close to the sea and the mountain. 
        You can both ski in winter and swim in summer.
        ```
        
        With maximum tokens = 6, these are the chunks created:
        ```
        Barcelona is a city in Spain.
        It is close to the sea. 
        and the mountain. 
        You can both ski in winter.
        and swim in summer.
        ```
        
        b) **With overlap approach:**
        
           Follow the same logic with no overlap approach, except that you create an overlap between chunks according to certain ratio.
           

## Learn more about embedding models in Azure OpenAI

+ [Understanding embeddings in Azure OpenAI Service](https://learn.microsoft.com/azure/cognitive-services/openai/concepts/understand-embeddings)
+ [Learn how to generate embeddings](https://learn.microsoft.com/azure/cognitive-services/openai/how-to/embeddings?tabs=console)
+ [Tutorial: Explore Azure OpenAI Service embeddings and document search](https://learn.microsoft.com/azure/cognitive-services/openai/tutorials/embeddings?tabs=command-line)
