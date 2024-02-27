---
page_type: sample
languages:
  - javascript
name: Vector search in Java
products:
  - azure
  - azure-cognitive-search
  - azure-openai
description: |
  Using azure-search-documents and Java, index and query vectors in a RAG pattern or a traditional search solution.
urlFragment: vector-search-java
---

# Vector search using Java  (Azure AI Search)  

The Java demo in this repository creates vectorized data on Azure AI Search. We recommend querying your vector data with Azure OpenAI Studio after your content is indexed.

| Samples | Description |
|---------|-------------|
| **integrated-vectorization** | [Integrated Vectorization sample](#run-the-integrated-vectorization-sample-program). It uses **azure-search-documents** in the Azure SDK for Java. It sets up [integrated vectorization](https://learn.microsoft.com/azure/search/vector-search-integrated-vectorization) on a [blob container](https://learn.microsoft.com/zure/search/search-blob-storage-integration). |

## Prerequisites

+ An Azure subscription, with [access to Azure OpenAI](https://aka.ms/oai/access). You must have the Azure OpenAI service name and an API key.

+ A deployment of the **text-embedding-ada-002** embedding model.

+ Azure Storage with a blob container containing sample data. We used the [NASA ebooks](https://github.com/Azure-Samples/azure-search-sample-data/tree/main/nasa-e-book) to test this sample.

+ Azure AI Search, any tier, but choose a service that has sufficient capacity for your vector index. We recommend Standard for the [NASA e-books](https://github.com/Azure-Samples/azure-search-sample-data/tree/main/nasa-e-book) sample data (the PDFs are large). If your search service is Basic, use smaller data files, such as [famous speeches](https://github.com/Azure-Samples/azure-search-sample-data/tree/main/famous-speeches-pdf).

+ A Java IDE. We used [Visual Studio Code](https://code.visualstudio.com/download) with the [Java Extension for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=vscjava.vscode-java-pack) to test this sample.

+ A Java JDK. We used [openjdk version 17.0.7](https://learn.microsoft.com/java/openjdk/download) to test this sample.

+ Maven (installed locally, with %MAVEN_PATH% system variable assigned to the path). We used [apache-maven-3.9.6](https://maven.apache.org/download.cgi) to test this sample.

## Set up your environment

1. Clone this repository or download the folder.

1. Rename `.env-sample` file in the /demo-java/integrated-vectorization/src/resources directory to `.env`.

1. Update the envrionment variables to point to your deployments.

## Run the integrated vectorization sample program

1. In Visual Studio Code, open the **integrated-vectorization** folder.

1. Start a new terminal session, and type `java -version` and `mvn -version` to confirm program availability.

   ![Screenshot of console showin test output.](../docs/media/java-sample-test-versions.png)

1. Run the following command: `mvn compile exec:java`

   A successful execution should have output similar to this example:
    
    ```bash
    PS C:\test\azure-search-vector-samples\demo-java\integrated-vectorization> mvn compile exec:java 
    [INFO] --- exec:3.1.1:java (default-cli) @ vectorsearchjavademo ---
    Created index
    Created datasource
    Created skillset
    Created and ran indexer
    [INFO] ------------------------------------------------------------------------
    [INFO] BUILD SUCCESS
    [INFO] ------------------------------------------------------------------------
    [INFO] Total time:  18.049 s
    [INFO] Finished at: 2024-02-27T12:40:14-08:00
    [INFO] ------------------------------------------------------------------------
    ```

1. [Sign in to the Azure portal](https://portal.azure.com) to confirm you have an index, indexer, data source, and skillset on Azure AI Search.

## Query your index in Azure OpenAI Studio

1. [Sign in to Azure OpenAI Studio](https://oai.azure.com/portal/).
1. On the left nav pane, under **Playground**, select **Chat**.
1. In the chat playground, select **Add your data**, and then select **Add a data source**.
1. Choose Azure AI Search.
1. On the wizard's first page, select your search service and the Java demo index you just created.
1. Select the **Add vector search to this search resource** and acknowledge the billing effect of using Azure AI Search.
1. Select an embedding model on your Azure OpenAI resource and acknowledge the billing effect.
1. On the wizard's next page, choose the query type and if using semantic ranking, acknowledge the billing effect. You might want to confirm [semantic ranker is enabled](https://learn.microsoft.com/azure/search/semantic-how-to-enable-disable) if you aren't sure.
1. On the wizard's last page, review and create.
1. On the **Configuration** tab to the right, choose **gpt-35-turbo** for the deployment.
1. Start your first chat with "what are natural sources of light at night?" and continue from there. You can modify settings on the chat playground's data source or in the **Configuration** tab to change the query behavior.

   :::image type="content" source="media/playground-chat.png" alt-text="Screeshot of the chat playground.":::
