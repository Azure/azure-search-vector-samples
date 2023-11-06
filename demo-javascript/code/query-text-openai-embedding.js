const axios = require("axios");  
const dotenv = require("dotenv");  
const fs = require("fs");  
const {  
  SearchClient,  
  AzureKeyCredential,  
} = require("@azure/search-documents");  
  
async function main() {  
  // Load environment variables from .env file  
  dotenv.config({ path: "../.env" });  
  
  // User input query  
  const userQuery = "what azure services support full text search";  
  
  // Generate embedding for the user query  
  console.log("Generating query embedding with Azure OpenAI...");  
  const queryEmbedding = await generateQueryEmbedding(userQuery);  
  console.log("Query embedding:", queryEmbedding);  
  
  // Output query embedding to queryVector.json file  
  fs.writeFileSync("../output/queryVector.json", JSON.stringify(queryEmbedding));  
  console.log("Success! See output/queryVector.json");  
  
  // Perform vector search using queryEmbedding  
  console.log("\nPerforming vector search...");  
  await performVectorSearch(queryEmbedding);  
  
  // Perform traditional text search without using raw vector query  
  console.log("\nPerforming traditional text search...");  
  await performTextSearch(userQuery);  
}  
  
// Function to generate embeddings using Azure Open AI  
async function generateQueryEmbedding(input) {  
  // Set Azure OpenAI API parameters from environment variables  
  const apiKey = process.env.AZURE_OPENAI_API_KEY;  
  const apiBase = `https://${process.env.AZURE_OPENAI_SERVICE_NAME}.openai.azure.com`;  
  const apiVersion = process.env.AZURE_OPENAI_API_VERSION;  
  const deploymentName = process.env.AZURE_OPENAI_DEPLOYMENT_NAME;  
  
  try {  
    const response = await axios.post(  
      `${apiBase}/openai/deployments/${deploymentName}/embeddings?api-version=${apiVersion}`,  
      {  
        input,  
        engine: "text-embedding-ada-002",  
      },  
      {  
        headers: {  
          "Content-Type": "application/json",  
          "api-key": apiKey,  
        },  
      }  
    );  
  
    const embedding = response.data.data[0].embedding;  
    return embedding;  
  } catch (error) {  
    console.error("Error generating query embedding: ", error.message);  
    throw error;  
  }  
}  
  
async function performVectorSearch(queryEmbedding) {  
  const searchServiceEndpoint = process.env.AZURE_SEARCH_ENDPOINT;  
  const searchServiceApiKey = process.env.AZURE_SEARCH_ADMIN_KEY;  
  const searchIndexName = process.env.AZURE_SEARCH_INDEX_NAME;  
  
  const searchClient = new SearchClient(  
    searchServiceEndpoint,  
    searchIndexName,  
    new AzureKeyCredential(searchServiceApiKey)  
  );  
  
  const response = await searchClient.search(undefined, {  
    vector: {  
      value: queryEmbedding,  
      kNearestNeighborsCount: 3,  
      fields: ["contentVector"],  
    },  
    select: ["title", "content", "category"],  
  });  
  
  console.log("\nVector search results:");  
  for await (const result of response.results) {  
    console.log(`Title: ${result.document.title}`);  
    console.log(`Score: ${result.score}`);  
    console.log(`Content: ${result.document.content}`);  
    console.log(`Category: ${result.document.category}`);  
    console.log("\n");  
  }  
}  
  
async function performTextSearch(query) {  
  const searchServiceEndpoint = process.env.AZURE_SEARCH_ENDPOINT;  
  const searchServiceApiKey = process.env.AZURE_SEARCH_ADMIN_KEY;  
  const searchIndexName = process.env.AZURE_SEARCH_INDEX_NAME;  
  
  const searchClient = new SearchClient(  
    searchServiceEndpoint,  
    searchIndexName,  
    new AzureKeyCredential(searchServiceApiKey)  
  );  
  
  const response = await searchClient.search(query, {  
    select: ["title", "content", "category"],  
    top: 3,  
  });  
  
  console.log("\nTraditional text search results:");  
  for await (const result of response.results) {  
    console.log(`Title: ${result.document.title}`);  
    console.log(`Score: ${result.score}`);  
    console.log(`Content: ${result.document.content}`);  
    console.log(`Category: ${result.document.category}`);  
    console.log("\n");  
  }  
}  
  
main();  
