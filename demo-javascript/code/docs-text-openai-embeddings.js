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
  
// Read the text-sample.json  
const input_data = JSON.parse(  
  fs.readFileSync("../data/text-sample.json", "utf-8")  
);  
  
// Function to generate embeddings for title and content fields  
async function generate_embeddings(text) {  
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
}  
  
(async () => {  
  // Generate embeddings for title and content fields  
  for (const item of input_data) {  
    const title = item.title;  
    const content = item.content;  
    const title_embeddings = await generate_embeddings(title);  
    const content_embeddings = await generate_embeddings(content);  
    item.titleVector = title_embeddings;  
    item.contentVector = content_embeddings;  
    item["@search.action"] = "upload";  
  }  
  
  // Output embeddings to docVectors.json file  
  fs.writeFileSync("../output/docVectors.json", JSON.stringify(input_data));  
})();  
