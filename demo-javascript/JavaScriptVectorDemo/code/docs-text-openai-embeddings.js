const axios = require("axios");
const dotenv = require("dotenv");
const fs = require("fs");

async function main() {
  // Load environment variables from .env file
  dotenv.config({ path: "../.env" });

  // Read data/text-sample.json
  console.log("Reading data/text-sample.json...");
  const inputData = JSON.parse(
    fs.readFileSync("../data/text-sample.json", "utf-8")
  );

  // Generate embeddings for title and content fields
  console.log("Generating embeddings with Azure OpenAI...");
  const outputData = [];
  for (const item of inputData) {
    const titleEmbeddings = await generateEmbeddings(item.title);
    const contentEmbeddings = await generateEmbeddings(item.content);

    outputData.push({
      ...item,
      titleVector: titleEmbeddings,
      contentVector: contentEmbeddings,
      "@search.action": "upload",
    });
  }

  // Output embeddings to docVectors.json file
  fs.writeFileSync("../output/docVectors.json", JSON.stringify(outputData));
  console.log("Success! See output/docVectors.json");
}

// Function to generate embeddings using Azure Open AI
async function generateEmbeddings(text) {
  // Set Azure OpenAI API parameters from environment variables
  const apiKey = process.env.AZURE_OPENAI_API_KEY;
  const apiBase = `https://${process.env.AZURE_OPENAI_SERVICE_NAME}.openai.azure.com`;
  const apiVersion = process.env.AZURE_OPENAI_API_VERSION;
  const deploymentName = process.env.AZURE_OPENAI_DEPLOYMENT_NAME;

  try {
    const response = await axios.post(
      `${apiBase}/openai/deployments/${deploymentName}/embeddings?api-version=${apiVersion}`,
      {
        input: text,
        engine: "text-embedding-ada-002",
      },
      {
        headers: {
          "Content-Type": "application/json",
          "api-key": apiKey,
        },
      }
    );

    const embeddings = response.data.data[0].embedding;
    return embeddings;
  } catch (error) {
    console.error("Error generating embeddings: ", error.message);
    throw error;
  }
}

main();
