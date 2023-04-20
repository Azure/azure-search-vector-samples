// Import libraries  
const axios = require("axios");  
const dotenv = require("dotenv");  
const fs = require("fs");  
  
// Load environment variables from .env file  
dotenv.config({ path: "../.env" });
  
// Set OpenAI API key and base URL from environment variables  
const apiKey = process.env.OPENAI_API_KEY;  
const apiBase = `https://${process.env.OPENAI_SERVICE_NAME}.openai.azure.com`;  
const apiVersion = process.env.OPENAI_API_VERSION;  
const deploymentName = process.env.DEPLOYMENT_NAME;
  
// User input query  
const userQuery = "what azure services support full text search";  
  
// Function to generate embeddings for a single query  
async function create_query_embedding(input) {  
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
    console.error("Error generating query embedding:", error.message);  
    return null;  
  }  
}  
  
(async () => {  
  // Generate embedding for the user query  
  const query_embedding = await create_query_embedding(userQuery);  
  
  if (query_embedding) {  
    console.log("Query Embedding:", query_embedding);  
  } else {  
    console.log("Failed to generate query embedding.");  
  }  

    // Output query embedding to queryVector.json file  
    fs.writeFileSync("../output/queryVector.json", JSON.stringify(query_embedding));  
})();  
