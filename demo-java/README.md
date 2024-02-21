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

The JavaScript demo in this repository creates vectorized data that can be indexed and queried on Azure AI Search.

| Samples | Description |
|---------|-------------|
| **integrated-vectorization** | [Integrated Vectorization sample](#run-the-integrated-vectorization-sample-program). It uses **azure-search-documents** in the Azure SDK for Java. It sets up [integrated vectorization](https://learn.microsoft.com/en-us/azure/search/vector-search-integrated-vectorization) on a [blob container](https://learn.microsoft.com/en-us/azure/search/search-blob-storage-integration). |

## Prerequisites

+ An Azure subscription, with [access to Azure OpenAI](https://aka.ms/oai/access). You must have the Azure OpenAI service name and an API key.

+ A deployment of the **text-embedding-ada-002** embedding model.

+ A Java IDE. We used [Visual Studio Code](https://code.visualstudio.com/download) with the [Java Extension for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=vscjava.vscode-java-pack) to test this sample.

+ A Java JDK. We used [openjdk version 17.0.7](https://learn.microsoft.com/java/openjdk/download) to test this sample.

+ Maven (installed locally, with %MAVEN_PATH% system variable assigned to the path). We used [apache-maven-3.9.6](https://maven.apache.org/download.cgi) to test this sample.

1. Clone this repository.

1. Copy the `.env-sample` file in the *integrated-vectorization/src/resources* directory to *integrated-vectorization/src/resources/.env* and update all the variables to point to your deployments

## Run the integrated vectorization sample program

1. In Visual Studio Code, open the **integrated-vectorization** folder.

1. Start a new terminal session, and type "java -version" and "mvn -version" to confirm program availability.

   ![Screenshot of console showin test output.](../docs/media/java-sample-test-versions.png)

1. Run the following command: `mvn compile exec:java`
