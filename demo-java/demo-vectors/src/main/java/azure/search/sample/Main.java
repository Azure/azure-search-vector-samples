// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

package azure.search.sample;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.ArrayList;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.InputStream;
import java.util.Scanner;


import com.azure.core.util.Context;
import com.azure.core.credential.AzureKeyCredential;
import com.azure.core.credential.TokenCredential;
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.search.documents.SearchClient;
import com.azure.search.documents.SearchClientBuilder;
import com.azure.search.documents.SearchDocument;
import com.azure.search.documents.models.QueryType;
import com.azure.search.documents.indexes.SearchIndexClient;
import com.azure.search.documents.indexes.SearchIndexClientBuilder;
import com.azure.ai.openai.OpenAIClient;
import com.azure.ai.openai.OpenAIClientBuilder;
import com.azure.ai.openai.models.EmbeddingItem;
import com.azure.ai.openai.models.Embeddings;
import com.azure.ai.openai.models.EmbeddingsOptions;
import com.azure.ai.openai.models.EmbeddingsUsage;
import com.azure.search.documents.indexes.SearchIndexerDataSources;
import com.azure.search.documents.indexes.models.AzureOpenAIVectorizer;
import com.azure.search.documents.indexes.models.AzureOpenAIParameters;
import com.azure.search.documents.indexes.models.HnswAlgorithmConfiguration;
import com.azure.search.documents.indexes.models.SearchField;
import com.azure.search.documents.indexes.models.SearchFieldDataType;
import com.azure.search.documents.indexes.models.SearchIndex;
import com.azure.search.documents.indexes.models.SemanticConfiguration;
import com.azure.search.documents.indexes.models.SemanticField;
import com.azure.search.documents.indexes.models.SemanticPrioritizedFields;
import com.azure.search.documents.indexes.models.SemanticSearch;
import com.azure.search.documents.indexes.models.VectorSearch;
import com.azure.search.documents.indexes.models.VectorSearchProfile;
import com.azure.search.documents.models.QueryAnswer;
import com.azure.search.documents.models.QueryAnswerResult;
import com.azure.search.documents.models.QueryAnswerType;
import com.azure.search.documents.models.QueryCaption;
import com.azure.search.documents.models.QueryCaptionResult;
import com.azure.search.documents.models.QueryCaptionType;
import com.azure.search.documents.models.SearchOptions;
import com.azure.search.documents.models.SearchResult;
import com.azure.search.documents.models.SemanticSearchOptions;
import com.azure.search.documents.models.VectorFilterMode;
import com.azure.search.documents.models.VectorQuery;
import com.azure.search.documents.models.VectorSearchOptions;
import com.azure.search.documents.models.VectorizedQuery;
import com.azure.search.documents.models.VectorizableTextQuery;
import com.azure.search.documents.util.SearchPagedIterable;
import java.util.stream.Collectors;
import java.util.concurrent.TimeUnit;

import io.github.cdimascio.dotenv.Dotenv;


public class Main {
    private static final String USER = "search-java-sample";

    public static void main(String[] args) throws InterruptedException {
        Dotenv dotenv = Dotenv.load();
        String endpoint = dotenv.get("AZURE_SEARCH_ENDPOINT");
        String key = dotenv.get("AZURE_SEARCH_ADMIN_KEY");
        String indexName = dotenv.get("AZURE_SEARCH_INDEX");
        String azureOpenAIEndpoint = dotenv.get("AZURE_OPENAI_ENDPOINT");
        String azureOpenAIEmbeddingDeployment = dotenv.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT");
        String azureOpenAIKey = dotenv.get("AZURE_OPENAI_KEY");

        TokenCredential tokenCredential = new DefaultAzureCredentialBuilder().build();
        var searchIndexClientBuilder = new SearchIndexClientBuilder()
            .endpoint(endpoint);
        if (!key.isBlank()) {
            searchIndexClientBuilder = searchIndexClientBuilder.credential(new AzureKeyCredential(key));
        } else {
            searchIndexClientBuilder = searchIndexClientBuilder.credential(tokenCredential);
        }

        SearchIndexClient searchIndexClient = searchIndexClientBuilder.buildClient();
         // Create the search index, including the new SearchFieldDataType.Single field for vector description.
        SearchIndex searchIndex = new SearchIndex(indexName)
            .setFields(
                new SearchField("id", SearchFieldDataType.STRING)
                    .setKey(true)
                    .setFilterable(true)
                    .setSortable(true),
                new SearchField("content", SearchFieldDataType.STRING)
                    .setSearchable(true),
                new SearchField("contentVector", SearchFieldDataType.collection(SearchFieldDataType.SINGLE))
                    .setSearchable(true)
                    .setVectorSearchDimensions(1536)
                    // This must match a vector search configuration name.
                    .setVectorSearchProfileName("my-vector-profile"),
                new SearchField("title", SearchFieldDataType.STRING)
                    .setSearchable(true),
                new SearchField("titleVector", SearchFieldDataType.collection(SearchFieldDataType.SINGLE))
                    .setSearchable(true)
                    .setVectorSearchDimensions(1536)
                    // This must match a vector search configuration name.
                    .setVectorSearchProfileName("my-vector-profile"),
                new SearchField("category", SearchFieldDataType.STRING)
                    .setSearchable(true)
                    .setFilterable(true))
            // VectorSearch configuration is required for a vector field.
            // The name used for the vector search algorithm configuration must match the configuration used by the
            // search field used for vector search.
            .setVectorSearch(new VectorSearch()
                .setProfiles(Collections.singletonList(
                    new VectorSearchProfile("my-vector-profile", "my-vector-config")
                        .setVectorizer("my-vectorizer")))
                .setAlgorithms(Collections.singletonList(
                    new HnswAlgorithmConfiguration("my-vector-config")))
                .setVectorizers(Collections.singletonList(
                    new AzureOpenAIVectorizer("my-vectorizer")
                        .setAzureOpenAIParameters(
                            new AzureOpenAIParameters()
                                .setResourceUri(azureOpenAIEndpoint)
                                .setDeploymentId(azureOpenAIEmbeddingDeployment)
                                .setApiKey(azureOpenAIKey))))
                )
            .setSemanticSearch(new SemanticSearch().setConfigurations(Arrays.asList(new SemanticConfiguration(
                "my-semantic-config", new SemanticPrioritizedFields()
                    .setContentFields(new SemanticField("content"))))));
            
        searchIndexClient.createOrUpdateIndex(searchIndex);
        System.out.println("Created index");

        var openAIClientBuilder = new OpenAIClientBuilder()
            .endpoint(azureOpenAIEndpoint);
        if (!azureOpenAIKey.isBlank()) {
            openAIClientBuilder = openAIClientBuilder
                .credential(new AzureKeyCredential(azureOpenAIKey));
        } else {
            openAIClientBuilder = openAIClientBuilder
                .credential(tokenCredential);
        }
        OpenAIClient openAIClient = openAIClientBuilder.buildClient();

        // Load JSON file from resources
        InputStream inputStream = Main.class.getResourceAsStream("/text-sample.json");
        // Parse JSON using org.json library
        JSONArray jsonArray = new JSONArray(new Scanner(inputStream).useDelimiter("\\A").next());

        var searchClientBuilder = new SearchClientBuilder()
            .endpoint(endpoint)
            .indexName(indexName);
        if (!key.isBlank()) {
            searchClientBuilder = searchClientBuilder.credential(new AzureKeyCredential(key));
        } else {
            searchClientBuilder = searchClientBuilder.credential(tokenCredential);
        }
        SearchClient searchClient = searchClientBuilder.buildClient();

        // Load documents from JSON array
        var contentTexts = new ArrayList<String>();
        var titleTexts = new ArrayList<String>();
        var searchDocuments = new ArrayList<SearchDocument>();
        for (int i = 0; i < jsonArray.length(); i++) {
            JSONObject jsonObject = jsonArray.getJSONObject(i);
            var doc = new SearchDocument();
            doc.put("title", jsonObject.getString("title"));
            doc.put("id", jsonObject.getString("id"));
            doc.put("content", jsonObject.getString("content"));
            doc.put("category", jsonObject.getString("category"));
            contentTexts.add(jsonObject.getString("content"));
            titleTexts.add(jsonObject.getString("title"));
            searchDocuments.add(doc);
        }

        System.out.println("Embedding documents...");
        embedTextAndUpdateDocuments(openAIClient, contentTexts, searchDocuments, "contentVector", azureOpenAIEmbeddingDeployment);
        embedTextAndUpdateDocuments(openAIClient, titleTexts, searchDocuments, "titleVector", azureOpenAIEmbeddingDeployment);

        searchClient.uploadDocuments(searchDocuments);
        System.out.println("Pausing after uploading documents...");
        // IMPORTANT - Pause for a few seconds to ensure the search service has the latest data
        TimeUnit.SECONDS.sleep(2);

        singleVectorSearchWithEmbedding(searchClient, openAIClient, "tools for software development", azureOpenAIEmbeddingDeployment);
        singleVectorSearch(searchClient, "tools for software development");
        singleVectorSearchWithFilter(searchClient, "tools for software development");
        simpleHybridSearch(searchClient, "scalable storage solution");
        semanticHybridSearch(searchClient, "scalable storage solution");
        semanticFullSearch(searchClient, "title:Azure AND \"scalable\"^3", "Azure scalable");
        multiVectorSearch(searchClient, "tools for software development");
    }

    private static void embedTextAndUpdateDocuments(OpenAIClient openAIClient, List<String> texts, List<SearchDocument> documents, String field, String azureOpenAIEmbeddingDeployment)
    {
        EmbeddingsOptions embeddingsOptions = new EmbeddingsOptions(texts)
            .setUser(USER);

        Embeddings embeddings = openAIClient.getEmbeddings(azureOpenAIEmbeddingDeployment, embeddingsOptions);
        int i = 0;
        for (EmbeddingItem item : embeddings.getData()) {
            documents.get(i).put(field, item.getEmbedding());
            i++;
        }
    }

      /**
     * Example of using vector search without any other search parameters, such as a search query or filters.
     * Generate the embedding using the OpenAI SDK
     */
    public static void singleVectorSearchWithEmbedding(SearchClient searchClient, OpenAIClient openAIClient, String query, String azureOpenAIEmbeddingDeployment) {
        EmbeddingsOptions embeddingsOptions = new EmbeddingsOptions(Arrays.asList(query))
            .setUser(USER);

        Embeddings embeddings = openAIClient.getEmbeddings(azureOpenAIEmbeddingDeployment, embeddingsOptions);
        List<Float> embedding = embeddings
            .getData()
            .get(0)
            .getEmbedding()
            .stream()
            .map(Double::floatValue)
            .collect(Collectors.toList());

        // Example of using vector search without using a search query or any filters.
        VectorQuery vectorizableQuery = new VectorizedQuery(embedding)
            .setKNearestNeighborsCount(3)
            // Set the fields to compare the vector against. This is a comma-delimited list of field names.
            .setFields("contentVector");

        SearchPagedIterable searchResults = searchClient.search(null, new SearchOptions()
                .setVectorSearchOptions(new VectorSearchOptions().setQueries(vectorizableQuery))
                .setTop(3),
            Context.NONE);

        System.out.println("===================================");
        System.out.println("Single Vector Search from Embedding Results:");
        System.out.println("===================================");
        for (SearchResult searchResult : searchResults) {
            SearchDocument doc = searchResult.getDocument(SearchDocument.class);
            System.out.printf("Score: %f, Title: %s: Content: %s%n", searchResult.getScore(), doc.get("title"), doc.get("content"));
        }
    }

    /*
     * Example of using vector search without any other search parameters, such as a search query or filters.
     * Generate the embedding using a vectorizer
     */
    public static void singleVectorSearch(SearchClient searchClient, String query) {
       // Example of using vector search without using a search query or any filters.
       VectorQuery vectorizableQuery = new VectorizableTextQuery(query)
        .setKNearestNeighborsCount(3)
        // Set the fields to compare the vector against. This is a comma-delimited list of field names.
        .setFields("contentVector");

        SearchPagedIterable searchResults = searchClient.search(null, new SearchOptions()
                .setVectorSearchOptions(new VectorSearchOptions().setQueries(vectorizableQuery))
                .setTop(3),
            Context.NONE);

        System.out.println("===================================");
        System.out.println("Single Vector Search from Vectorizer Results:");
        System.out.println("===================================");
        for (SearchResult searchResult : searchResults) {
            SearchDocument doc = searchResult.getDocument(SearchDocument.class);
            System.out.printf("Score: %f, Title: %s: Content: %s%n", searchResult.getScore(), doc.get("title"), doc.get("content"));
        }
    }

     /**
     * Example of using vector search with a filter.
     */
    public static void singleVectorSearchWithFilter(SearchClient searchClient, String query) {
        // Example of using vector search with a filter.
        VectorQuery vectorizableQuery = new VectorizableTextQuery(query)
            .setKNearestNeighborsCount(3)
            // Set the fields to compare the vector against. This is a comma-delimited list of field names.
            .setFields("contentVector");

        SearchPagedIterable searchResults = searchClient.search(null, new SearchOptions()
            .setVectorSearchOptions(new VectorSearchOptions()
                .setQueries(vectorizableQuery))
                .setTop(3)
                .setFilter("category eq 'Developer Tools'"),
            Context.NONE);

        System.out.println("===================================");
        System.out.println("Single Vector Search With Filter Results:");
        System.out.println("===================================");
        for (SearchResult searchResult : searchResults) {
            SearchDocument doc = searchResult.getDocument(SearchDocument.class);
            System.out.printf("Score: %f, Title: %s: Content: %s%n", searchResult.getScore(), doc.get("title"), doc.get("content"));
        }
    }

    /**
     * Example of using vector search with a query in addition to vectorization.
     */
    public static void simpleHybridSearch(SearchClient searchClient, String query) {
        // Example of using vector search with a query in addition to vectorization.
        VectorQuery vectorizableQuery = new VectorizableTextQuery(query)
            .setKNearestNeighborsCount(3)
            // Set the fields to compare the vector against. This is a comma-delimited list of field names.
            .setFields("contentVector");

        SearchPagedIterable searchResults = searchClient.search("scalable storage solution", new SearchOptions()
            .setVectorSearchOptions(new VectorSearchOptions()
                .setQueries(vectorizableQuery))
            .setTop(3),
            Context.NONE);

        System.out.println("===================================");
        System.out.println("Simple Hybrid Search Results:");
        System.out.println("===================================");
        for (SearchResult searchResult : searchResults) {
            SearchDocument doc = searchResult.getDocument(SearchDocument.class);
            System.out.printf("Score: %f, Title: %s: Content: %s%n", searchResult.getScore(), doc.get("title"), doc.get("content"));
        }
    }

    /**
     * Example of using vector search with a semantic query in addition to vectorization.
     *
     */
    public static void semanticHybridSearch(SearchClient searchClient, String query) {
        // Example of using vector search with a semantic query in addition to vectorization.
        VectorQuery vectorizableQuery = new VectorizableTextQuery(query)
            .setKNearestNeighborsCount(3)
            // Set the fields to compare the vector against. This is a comma-delimited list of field names.
            .setFields("contentVector");

        SearchOptions searchOptions = new SearchOptions()
            .setVectorSearchOptions(new VectorSearchOptions()
                .setQueries(vectorizableQuery))
            .setTop(3)
            .setQueryType(QueryType.SEMANTIC)
            .setSemanticSearchOptions(new SemanticSearchOptions()
                .setSemanticConfigurationName("my-semantic-config")
                .setQueryAnswer(new QueryAnswer(QueryAnswerType.EXTRACTIVE))
                .setQueryCaption(new QueryCaption(QueryCaptionType.EXTRACTIVE)));

        SearchPagedIterable results = searchClient.search(
            "what is azure search?",
            searchOptions, Context.NONE);

        System.out.println("===================================");
        System.out.println("Semantic Hybrid Search Results:");
        System.out.println("===================================");

        System.out.println("Query Answer:");
        for (QueryAnswerResult result : results.getSemanticResults().getQueryAnswers()) {
            System.out.println("Answer Highlights: " + result.getHighlights());
            System.out.println("Answer Text: " + result.getText());
        }

        for (SearchResult result : results) {
            SearchDocument doc = result.getDocument(SearchDocument.class);
            System.out.printf("Score: %f, Title: %s: Content: %s%n", result.getScore(), doc.get("title"), doc.get("content"));

            if (result.getSemanticSearch().getQueryCaptions() != null) {
                QueryCaptionResult caption = result.getSemanticSearch().getQueryCaptions().get(0);
                if (!caption.getHighlights().isBlank()) {
                    System.out.println("Caption Highlights: " + caption.getHighlights());
                } else {
                    System.out.println("Caption Text: " + caption.getText());
                }
            }
        }
    }

        /**
     * Example of using vector search with a semantic query and full lucene query syntax in addition to vectorization.
     *
     */
    public static void semanticFullSearch(SearchClient searchClient, String fullQuery, String semanticQuery) {
        SearchOptions searchOptions = new SearchOptions()
            .setTop(3)
            .setQueryType(QueryType.FULL)
            .setSemanticSearchOptions(new SemanticSearchOptions()
                // Set a separate search query that will be solely used for semantic reranking, semantic captions and semantic answers.
                .setSemanticQuery(semanticQuery)
                .setSemanticConfigurationName("my-semantic-config")
                .setQueryAnswer(new QueryAnswer(QueryAnswerType.EXTRACTIVE))
                .setQueryCaption(new QueryCaption(QueryCaptionType.EXTRACTIVE)));

        SearchPagedIterable results = searchClient.search(
            fullQuery,
            searchOptions, Context.NONE);

        System.out.println("===================================");
        System.out.println("Semantic Full Text Search Results:");
        System.out.println("===================================");

        System.out.println("Query Answer:");
        for (QueryAnswerResult result : results.getSemanticResults().getQueryAnswers()) {
            System.out.println("Answer Highlights: " + result.getHighlights());
            System.out.println("Answer Text: " + result.getText());
        }

        for (SearchResult result : results) {
            SearchDocument doc = result.getDocument(SearchDocument.class);
            System.out.printf("Score: %f, Title: %s: Content: %s%n", result.getScore(), doc.get("title"), doc.get("content"));

            if (result.getSemanticSearch().getQueryCaptions() != null) {
                QueryCaptionResult caption = result.getSemanticSearch().getQueryCaptions().get(0);
                if (!caption.getHighlights().isBlank()) {
                    System.out.println("Caption Highlights: " + caption.getHighlights());
                } else {
                    System.out.println("Caption Text: " + caption.getText());
                }
            }
        }
    }

    /**
     * Example of using multiple vectors in vector search
     *
     */
    public static void multiVectorSearch(SearchClient searchClient, String query) {
        // Example of using multiple vectors in search without using a search query or any filters.
        VectorQuery firstVectorizableQuery = new VectorizableTextQuery(query)
            .setKNearestNeighborsCount(3)
            // Set the fields to compare the vector against. This is a comma-delimited list of field names.
            .setFields("contentVector");

        VectorQuery secondVectorizableQuery = new VectorizableTextQuery(query)
            .setKNearestNeighborsCount(3)
            // Set the fields to compare the vector against. This is a comma-delimited list of field names.
            .setFields("titleVector");

        SearchPagedIterable searchResults = searchClient.search(null, new SearchOptions()
            .setVectorSearchOptions(new VectorSearchOptions()
                .setQueries(firstVectorizableQuery, secondVectorizableQuery))
            .setTop(3),
            Context.NONE);

            System.out.println("===================================");
            System.out.println("Multi Vector Search Results:");
            System.out.println("===================================");
        for (SearchResult searchResult : searchResults) {
            SearchDocument doc = searchResult.getDocument(SearchDocument.class);
            System.out.printf("Score: %f, Title: %s: Content: %s%n", searchResult.getScore(), doc.get("title"), doc.get("content"));
        }
    }
}