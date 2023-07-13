const axios = require("axios");
const dotenv = require("dotenv");
const fs = require("fs");

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

main();
