---
page_type: sample
languages:
  - javas
name: Vector search in Java
products:
  - azure
  - azure-cognitive-search
  - azure-openai
description: |
  Using azure-search-documents and Java, index and query vectors in a RAG pattern or a traditional search solution.
urlFragment: vector-search-java
---

# Basic vector demo using Java (Azure AI Search)  

The Java demo in this repository creates vectorized data on Azure AI Search and runs a series of queries, sending output to the terminal window.

+ Create an index schema
+ Load the sample data
+ Embed the documents in-memory
+ Index the vector and nonvector fields
+ Run a series of vector and hybrid queries

The sample data is a JSON file of 108 descriptions of various Azure services. The descriptions are short, which makes data chunking unnecessary.

The queries are articulated as strings. An Azure OpenAI embedding model converts the strings to vectors at run time. Queries include a pure vector query, vector with fitlers, hybrid query, hybrid with semantic ranking, and a multivector query.

For further exploration and chat interaction, connect to your index using Azure OpenAI Studio.

## Prerequisites

+ An Azure subscription, with [access to Azure OpenAI](https://aka.ms/oai/access). You must have the Azure OpenAI service name and an API key.

+ A deployment of the **text-embedding-ada-002** embedding model.

+ Azure AI Search, any tier, but choose a service that has sufficient capacity for your vector index. We recommend Basic or higher.

+ A Java IDE. We used [Visual Studio Code](https://code.visualstudio.com/download) with the [Java Extension for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=vscjava.vscode-java-pack) to test this sample.

+ A Java JDK. We used [openjdk version 17.0.7](https://learn.microsoft.com/java/openjdk/download) to test this sample.

+ Maven (installed locally, with %MAVEN_PATH% system variable assigned to the path). We used [apache-maven-3.9.6](https://maven.apache.org/download.cgi) to test this sample.

## Set up your environment

1. Clone this repository or download the folder.

1. Rename `.env-sample` file in the /demo-java/demo-vectors/src/resources directory to `.env`.

1. Update the envrionment variables to point to your deployments.

## Run the vector demo sample program

1. In Visual Studio Code, open the **demo-vectors** folder.

1. Start a new terminal session, and type `java -version` and `mvn -version` to confirm program availability.

1. Run the following command: `mvn compile exec:java`

   A successful execution should have output similar to this example:

    ```bash
    PS C:\test\azure-search-vector-samples\demo-java\demo-vectors> mvn compile exec:java
    [INFO] --- exec:3.1.1:java (default-cli) @ vectordemo ---
    Created index
    Embedding documents...
    Pausing after uploading documents...
    ===================================
    Single Vector Search from Embedding Results:
    ===================================
    Score: 0.829682, Title: Azure DevOps: Content: Azure DevOps is a suite of services that help you plan, build, and deploy applications. It includes Azure Boards for work item tracking, Azure Repos for source code management, Azure Pipelines for continuous integration and continuous deployment, Azure Test Plans for manual and automated testing, and Azure Artifacts for package management. DevOps supports a wide range of programming languages, frameworks, and platforms, making it easy to integrate with your existing development tools and processes. It also integrates with other Azure services, such as Azure App Service and Azure Functions.
    
    . . .
    ```

1. [Sign in to the Azure portal](https://portal.azure.com) to confirm you have an index on Azure AI Search.

## Query your index in Azure OpenAI Studio

1. [Sign in to Azure OpenAI Studio](https://oai.azure.com/portal/).
1. On the left nav pane, under **Playground**, select **Chat**.
1. In the chat playground, select **Add your data**, and then select **Add a data source**.
1. Choose **Azure AI Search**.
1. On the wizard's first page, select your search service and the Java demo index you just created.
1. Select the **Add vector search to this search resource** and acknowledge the billing effect of using Azure AI Search.
1. Select an embedding model on your Azure OpenAI resource and acknowledge the billing effect.
1. **Important**. Select the **Use custom field mapping** checkbox. It adds a page for data field mapping. This step is important if you have multiple vector fields in the index.
1. Verify that both vector fields are listed in the data field mapping page.
1. On the wizard's next page, choose the query type and if using semantic ranking, acknowledge the billing effect. You might want to confirm [semantic ranker is enabled](https://learn.microsoft.com/azure/search/semantic-how-to-enable-disable) if you aren't sure.
1. On the wizard's last page, review and create.
1. On the **Configuration** tab to the right, choose **gpt-35-turbo** for the deployment.
1. Start your first chat with "How many Azure services store data" and continue from there. You can modify settings on the chat playground's data source or in the **Configuration** tab to change the query behavior.

![Screenshot of the chat playground](https://github.com/Azure/azure-search-vector-samples/blob/main/demo-java/media/playground-chat-azure-services.png?raw=true)
