// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

package azure.search.sample;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import org.xml.sax.ext.LexicalHandler;

import com.azure.core.credential.AzureKeyCredential;
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.search.documents.indexes.SearchIndexClient;
import com.azure.search.documents.indexes.SearchIndexerClient;
import com.azure.search.documents.indexes.SearchIndexClientBuilder;
import com.azure.search.documents.indexes.SearchIndexerClientBuilder;
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
import com.azure.search.documents.indexes.models.SearchIndexerDataSourceConnection;
import com.azure.search.documents.indexes.models.VectorSearch;
import com.azure.search.documents.indexes.models.VectorSearchProfile;
import com.azure.search.documents.indexes.models.InputFieldMappingEntry;
import com.azure.search.documents.indexes.models.AzureOpenAIEmbeddingSkill;
import com.azure.search.documents.indexes.models.SplitSkill;
import com.azure.search.documents.indexes.models.LexicalAnalyzerName;
import com.azure.search.documents.indexes.models.OutputFieldMappingEntry;
import com.azure.search.documents.indexes.models.SearchIndexerSkill;
import com.azure.search.documents.indexes.models.SearchIndexerSkillset;
import com.azure.search.documents.indexes.models.SearchIndexerIndexProjections;
import com.azure.search.documents.indexes.models.SearchIndexerIndexProjectionSelector;
import com.azure.search.documents.indexes.models.SearchIndexerIndexProjectionsParameters;
import com.azure.search.documents.indexes.models.IndexProjectionMode;
import com.azure.search.documents.indexes.models.SearchIndexer;
import com.azure.search.documents.indexes.models.TextSplitMode;

import io.github.cdimascio.dotenv.Dotenv;


public class Main {
    public static void main(String[] args) {
        Dotenv dotenv = Dotenv.load();
        String endpoint = dotenv.get("AZURE_SEARCH_ENDPOINT");
        String key = dotenv.get("AZURE_SEARCH_ADMIN_KEY");
        String indexName = dotenv.get("AZURE_SEARCH_INDEX");
        String dataSourceName = dotenv.get("AZURE_SEARCH_DATASOURCE");
        String skillsetName = dotenv.get("AZURE_SEARCH_SKILLSET");
        String indexerName = dotenv.get("AZURE_SEARCH_INDEXER");
        String azureOpenAIEndpoint = dotenv.get("AZURE_OPENAI_ENDPOINT");
        String azureOpenAIEmbeddingDeployment = dotenv.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT");
        String azureOpenAIKey = dotenv.get("AZURE_OPENAI_KEY");
        String blobContainerName = dotenv.get("BLOB_CONTAINER_NAME");
        String blobConnectionString = dotenv.get("BLOB_CONNECTION_STRING");

        var searchIndexClientBuilder = new SearchIndexClientBuilder()
            .endpoint(endpoint);
        if (!key.isBlank()) {
            searchIndexClientBuilder = searchIndexClientBuilder.credential(new AzureKeyCredential(key));
        } else {
            searchIndexClientBuilder = searchIndexClientBuilder.credential(new DefaultAzureCredentialBuilder().build());
        }

        SearchIndexClient searchIndexClient = searchIndexClientBuilder.buildClient();
         // Create the search index, including the new SearchFieldDataType.Single field for vector description.
        SearchIndex searchIndex = new SearchIndex(indexName)
            .setFields(
                new SearchField("chunk_id", SearchFieldDataType.STRING)
                    .setKey(true)
                    .setFilterable(true)
                    .setSortable(true)
                    .setAnalyzerName(LexicalAnalyzerName.KEYWORD),
                new SearchField("title", SearchFieldDataType.STRING)
                    .setSearchable(true),
                new SearchField("vector", SearchFieldDataType.collection(SearchFieldDataType.SINGLE))
                    .setSearchable(true)
                    .setVectorSearchDimensions(1536)
                    // This must match a vector search configuration name.
                    .setVectorSearchProfileName("my-vector-profile"),
                new SearchField("parent_id", SearchFieldDataType.STRING)
                    .setFilterable(true)
                    .setSortable(true),
                new SearchField("chunk", SearchFieldDataType.STRING))

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
                    .setTitleField(new SemanticField("title"))
                    .setContentFields(new SemanticField("chunk"))))));
            
        searchIndexClient.createOrUpdateIndex(searchIndex);
        System.out.println("Created index");

        var searchIndexerClientBuilder = new SearchIndexerClientBuilder()
            .endpoint(endpoint);
        if (!key.isBlank()) {
            searchIndexerClientBuilder = searchIndexerClientBuilder.credential(new AzureKeyCredential(key));
        } else {
            searchIndexerClientBuilder = searchIndexerClientBuilder.credential(new DefaultAzureCredentialBuilder().build());
        }

        SearchIndexerClient searchIndexerClient = searchIndexerClientBuilder.buildClient();
        SearchIndexerDataSourceConnection dataSourceConnection = SearchIndexerDataSources.createFromAzureBlobStorage(
            dataSourceName,
            blobConnectionString,
            blobContainerName,
            null,
            null,
            null
        );
        searchIndexerClient.createOrUpdateDataSourceConnection(dataSourceConnection);
        System.out.println("Created datasource");

        var skillset = new SearchIndexerSkillset(skillsetName)
            .setSkills(
                Arrays.asList(
                    createEmbeddingSkill(azureOpenAIEndpoint, azureOpenAIEmbeddingDeployment, azureOpenAIKey),
                    createSplitSkill())
                )
            .setIndexProjections(
                new SearchIndexerIndexProjections(
                    Collections.singletonList(
                        new SearchIndexerIndexProjectionSelector(
                            indexName,
                            "parent_id",
                            "/document/pages/*",
                            Arrays.asList(
                                new InputFieldMappingEntry("chunk")
                                    .setSource("/document/pages/*"),
                                new InputFieldMappingEntry("vector")
                                    .setSource("/document/pages/*/vector"),
                                new InputFieldMappingEntry("title")
                                    .setSource("/document/metadata_storage_name")
                            )
                        )
                    )
                )
                .setParameters(
                    new SearchIndexerIndexProjectionsParameters()
                        .setProjectionMode(IndexProjectionMode.SKIP_INDEXING_PARENT_DOCUMENTS)
                )
            );
        searchIndexerClient.createOrUpdateSkillset(skillset);
        System.out.println("Created skillset");

        var indexer = new SearchIndexer(indexerName)
            .setTargetIndexName(indexName)
            .setDataSourceName(dataSourceName)
            .setSkillsetName(skillsetName);
        searchIndexerClient.createOrUpdateIndexer(indexer);
        searchIndexerClient.runIndexer(indexerName);
        System.out.println("Created and ran indexer");
    }

    private static AzureOpenAIEmbeddingSkill createEmbeddingSkill(String resourceUri, String deploymentId, String key) {
        List<InputFieldMappingEntry> inputs = Collections.singletonList(
            new InputFieldMappingEntry("text")
                .setSource("/document/pages/*")
        );

        List<OutputFieldMappingEntry> outputs = Collections.singletonList(
            new OutputFieldMappingEntry("embedding")
                .setTargetName("vector")
        );

        return new AzureOpenAIEmbeddingSkill(inputs, outputs)
            .setResourceUri(resourceUri)
            .setDeploymentId(deploymentId)
            .setApiKey(key)
            .setContext("/document/pages/*");
    }

    private static SplitSkill createSplitSkill() {
        List<InputFieldMappingEntry> inputs = Collections.singletonList(
            new InputFieldMappingEntry("text")
                .setSource("/document/content")
        );

        List<OutputFieldMappingEntry> outputs = Collections.singletonList(
            new OutputFieldMappingEntry("textItems")
                .setTargetName("pages")
        );

        return new SplitSkill(inputs, outputs)
            .setContext("/document")
            .setTextSplitMode(TextSplitMode.PAGES)
            .setMaximumPageLength(2000)
            .setPageOverlapLength(500);
    }
}