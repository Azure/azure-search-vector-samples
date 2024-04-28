const dotenv = require("dotenv");
const fs = require("fs");
const { SearchIndexClient, SearchClient } = require("@azure/search-documents");
const { DefaultAzureCredential } = require("@azure/identity")
const { AzureKeyCredential } = require("@azure/core-auth")
const { OpenAIClient } = require("@azure/openai");
const { promisify } = require('util');
const { program } = require('commander');
const { create } = require("domain");

program
  .option('-e, --embed', 'Recreate embeddings in text-sample.json')
  .option('-u, --upload', 'Upload embeddings and data in text-sample.json to the search index');

async function main() {
  program.parse();

  const options = program.opts()
  const defaultCredential = new DefaultAzureCredential();

  // Load environment variables from .env file
  dotenv.config({ path: "../.env" });

  // Create Azure AI Search index
  try {
    await createSearchIndex(defaultCredential);
  } catch (err) {
    console.error(`Failed to create ACS index: ${err.message}`);
    return;
  }

  // Generate document embeddings
  if (options.embed) {
    try {
      await generateDocumentEmbeddings(defaultCredential);
    } catch (err) {
      console.error(
        `Failed to generate embeddings: ${err.message}`
      );
      return;
    }
  }

  // Upload documents to Azure AI Search
  if (options.upload) {
    try {
      await uploadDocuments(defaultCredential);
    } catch (err) {
      console.error(
        `Failed to upload documents to search index: ${err.message}`
      );
      return;
    }
  }
}

  /*
  // Examples of different types of vector searches
  await doPureVectorSearch();
  await doPureVectorSearchMultilingual();
  await doCrossFieldVectorSearch();
  await doVectorSearchWithFilter();
  await doHybridSearch();
  await doSemanticHybridSearch();
  */

const readFileAsync = promisify(fs.readFile);
const writeFileAsync = promisify(fs.writeFile);

async function generateDocumentEmbeddings(defaultCredential) {
  const openAiEndpoint = process.env.AZURE_OPENAI_ENDPOINT;
  const openAiKey = process.env.AZURE_OPENAI_KEY;
  const openAiDeployment = process.env.AZURE_OPENAI_EMBEDDING_DEPLOYMENT;
  let credential = !openAiKey || openAiKey.trim() == '' ?
    defaultCredential : new AzureKeyCredential(openAiKey);
  const client = new OpenAIClient(openAiEndpoint, credential);

  console.log("Reading data/text-sample.json...");
  const fileData = await readFileAsync("../data/text-sample.json", "utf-8");
  let data = JSON.parse(fileData);

  console.log("Generating embeddings with Azure OpenAI...");
  const titles = data.map(item => item["title"]);
  const content = data.map(item => item["content"]);
  const titleEmbeddings = await client.getEmbeddings(openAiDeployment, titles);
  const contentEmbeddings = await client.getEmbeddings(openAiDeployment, content);

  for (let i = 0; i < data.length; i++) {
    data[i]["titleVector"] = titleEmbeddings.data[i].embedding;
    data[i]["contentVector"] = contentEmbeddings.data[i].embedding;
  }

  await writeFileAsync("../data/text-sample.json", JSON.stringify(data, null, 2));
}

async function createSearchIndex(defaultCredential) {
  const searchServiceEndpoint = process.env.AZURE_SEARCH_SERVICE_ENDPOINT;
  const searchServiceApiKey = process.env.AZURE_SEARCH_ADMIN_KEY;
  const searchIndexName = process.env.AZURE_SEARCH_INDEX;
  const embeddingDimensions = parseInt(process.env.AZURE_OPENAI_EMBEDDING_DIMENSIONS);

  let vectorSearchDimensions = isNaN(embeddingDimensions) || embeddingDimensions <= 0 ?
    1536 : embeddingDimensions;
  let credential = !searchServiceApiKey || searchServiceApiKey.trim() === '' ?
    defaultCredential : new AzureKeyCredential(searchServiceApiKey);

  const indexClient = new SearchIndexClient(
    searchServiceEndpoint,
    credential
  );

  const index = {
    name: searchIndexName,
    fields: [
      {
        name: "id",
        type: "Edm.String",
        key: true,
        sortable: true,
        filterable: true,
        facetable: true,
      },
      { name: "title", type: "Edm.String", searchable: true },
      { name: "content", type: "Edm.String", searchable: true },
      {
        name: "category",
        type: "Edm.String",
        filterable: true,
        searchable: true,
      },
      {
        name: "titleVector",
        type: "Collection(Edm.Single)",
        searchable: true,
        vectorSearchDimensions: vectorSearchDimensions,
        vectorSearchProfileName: "myHnswProfile",
      },
      {
        name: "contentVector",
        type: "Collection(Edm.Single)",
        searchable: true,
        vectorSearchDimensions: vectorSearchDimensions,
        vectorSearchProfileName: "myHnswProfile",
      },
    ],
    vectorSearch: {
      algorithms: [{ name: "myHnswAlgorithm", kind: "hnsw" }],
      profiles: [
        {
          name: "myHnswProfile",
          algorithmConfigurationName: "myHnswAlgorithm",
        },
      ],
    },
    semanticSearch: {
      configurations: [
        {
          name: "my-semantic-config",
          prioritizedFields: {
            contentFields: [{ name: "content" }],
            keywordsFields: [{ name: "category" }],
            titleField: {
              name: "title",
            },
          },
        },
      ],
    },
  };

  console.log("Creating ACS index...");
  await indexClient.createOrUpdateIndex(index);
}

function createSearchClient(defaultCredential) {
  const searchServiceEndpoint = process.env.AZURE_SEARCH_SERVICE_ENDPOINT;
  const searchServiceApiKey = process.env.AZURE_SEARCH_ADMIN_KEY;
  const searchIndexName = process.env.AZURE_SEARCH_INDEX;

  let credential = !searchServiceApiKey || searchServiceApiKey.trim() === '' ?
    defaultCredential : new AzureKeyCredential(searchServiceApiKey);

  return new SearchClient(
    searchServiceEndpoint,
    searchIndexName,
    credential
  );
}

async function uploadDocuments(defaultCredential) {
  console.log("Reading data/text-sample.json...");
  const fileData = await readFileAsync("../data/text-sample.json", "utf-8");
  let data = JSON.parse(fileData);

  const searchClient = createSearchClient(defaultCredential);

  console.log("Uploading documents to ACS index...");
  for (let i = 0; i < data.length; i++) {
    await searchClient.uploadDocuments([data[i]]);
  }
}

async function doPureVectorSearch() {
  const searchServiceEndpoint = process.env.AZURE_SEARCH_ENDPOINT;
  const searchServiceApiKey = process.env.AZURE_SEARCH_ADMIN_KEY;
  const searchIndexName = process.env.AZURE_SEARCH_INDEX_NAME;

  const searchClient = new SearchClient(
    searchServiceEndpoint,
    searchIndexName,
    new AzureKeyCredential(searchServiceApiKey)
  );

  const query = "tools for software development";
  const response = await searchClient.search(undefined, {
    vectorQueries: [{
      kind: "vector",
      vector: await generateEmbeddings(query),
      kNearestNeighborsCount: 3,
      fields: ["contentVector"],
    }],
    select: ["title", "content", "category"],
  });

  console.log(`\nPure vector search results:`);
  for await (const result of response.results) {
    console.log(`Title: ${result.document.title}`);
    console.log(`Score: ${result.score}`);
    console.log(`Content: ${result.document.content}`);
    console.log(`Category: ${result.document.category}`);
    console.log(`\n`);
  }
}

async function doPureVectorSearchMultilingual() {
  const searchServiceEndpoint = process.env.AZURE_SEARCH_ENDPOINT;
  const searchServiceApiKey = process.env.AZURE_SEARCH_ADMIN_KEY;
  const searchIndexName = process.env.AZURE_SEARCH_INDEX_NAME;

  const searchClient = new SearchClient(
    searchServiceEndpoint,
    searchIndexName,
    new AzureKeyCredential(searchServiceApiKey)
  );

  // e.g 'tools for software development' in Dutch)
  const query = "tools voor softwareontwikkeling";
  const response = await searchClient.search(undefined, {
    vectorQueries: [{
      kind: "vector",
      vector: await generateEmbeddings(query),
      kNearestNeighborsCount: 3,
      fields: ["contentVector"],
    }],
    select: ["title", "content", "category"],
  });

  console.log(`\nPure vector search (multilingual) results:`);
  for await (const result of response.results) {
    console.log(`Title: ${result.document.title}`);
    console.log(`Score: ${result.score}`);
    console.log(`Content: ${result.document.content}`);
    console.log(`Category: ${result.document.category}`);
    console.log(`\n`);
  }
}

async function doCrossFieldVectorSearch() {
  const searchServiceEndpoint = process.env.AZURE_SEARCH_ENDPOINT;
  const searchServiceApiKey = process.env.AZURE_SEARCH_ADMIN_KEY;
  const searchIndexName = process.env.AZURE_SEARCH_INDEX_NAME;

  const searchClient = new SearchClient(
    searchServiceEndpoint,
    searchIndexName,
    new AzureKeyCredential(searchServiceApiKey)
  );

  const query = "tools for software development";
  const response = await searchClient.search(undefined, {
    vectorQueries: [{
      kind: "vector",
      vector: await generateEmbeddings(query),
      kNearestNeighborsCount: 3,
      fields: ["titleVector", "contentVector"],
    }],
    select: ["title", "content", "category"],
  });

  console.log(`\nCross-field vector search results:`);
  for await (const result of response.results) {
    console.log(`Title: ${result.document.title}`);
    console.log(`Score: ${result.score}`);
    console.log(`Content: ${result.document.content}`);
    console.log(`Category: ${result.document.category}`);
    console.log(`\n`);
  }
}

async function doVectorSearchWithFilter() {
  const searchServiceEndpoint = process.env.AZURE_SEARCH_ENDPOINT;
  const searchServiceApiKey = process.env.AZURE_SEARCH_ADMIN_KEY;
  const searchIndexName = process.env.AZURE_SEARCH_INDEX_NAME;

  const searchClient = new SearchClient(
    searchServiceEndpoint,
    searchIndexName,
    new AzureKeyCredential(searchServiceApiKey)
  );

  const query = "tools for software development";
  const response = await searchClient.search(undefined, {
    vectorQueries: [{
      kind: "vector",
      vector: await generateEmbeddings(query),
      kNearestNeighborsCount: 3,
      fields: ["contentVector"],
    }],
    filter: "category eq 'Developer Tools'",
    select: ["title", "content", "category"],
  });

  console.log(`\nVector search with filter results:`);
  for await (const result of response.results) {
    console.log(`Title: ${result.document.title}`);
    console.log(`Score: ${result.score}`);
    console.log(`Content: ${result.document.content}`);
    console.log(`Category: ${result.document.category}`);
    console.log(`\n`);
  }
}

async function doHybridSearch() {
  const searchServiceEndpoint = process.env.AZURE_SEARCH_ENDPOINT;
  const searchServiceApiKey = process.env.AZURE_SEARCH_ADMIN_KEY;
  const searchIndexName = process.env.AZURE_SEARCH_INDEX_NAME;

  const searchClient = new SearchClient(
    searchServiceEndpoint,
    searchIndexName,
    new AzureKeyCredential(searchServiceApiKey)
  );

  const query = "scalable storage solution";
  const response = await searchClient.search(query, {
    vectorQueries: [{
      kind: "vector",
      vector: await generateEmbeddings(query),
      kNearestNeighborsCount: 3,
      fields: ["contentVector"],
    }],
    select: ["title", "content", "category"],
    top: 3,
  });

  console.log(`\nHybrid search results:`);
  for await (const result of response.results) {
    console.log(`Title: ${result.document.title}`);
    console.log(`Score: ${result.score}`);
    console.log(`Content: ${result.document.content}`);
    console.log(`Category: ${result.document.category}`);
    console.log(`\n`);
  }
}

async function doSemanticHybridSearch() {
  const searchServiceEndpoint = process.env.AZURE_SEARCH_ENDPOINT;
  const searchServiceApiKey = process.env.AZURE_SEARCH_ADMIN_KEY;
  const searchIndexName = process.env.AZURE_SEARCH_INDEX_NAME;

  const searchClient = new SearchClient(
    searchServiceEndpoint,
    searchIndexName,
    new AzureKeyCredential(searchServiceApiKey)
  );

  const query = "what is azure sarch?";
  const response = await searchClient.search(query, {
    vectorQueries: [{
      kind: "vector",
      vector: await generateEmbeddings(query),
      kNearestNeighborsCount: 3,
      fields: ["contentVector"],
    }],
    select: ["title", "content", "category"],
    queryType: "semantic",
    top: 3,
    semanticSearchOptions: {
      answers: {
          answerType: "extractive",
          count: 3
      },
      captions:{
          captionType: "extractive",
          count: 3
      },
      configurationName: "my-semantic-config",
    }
  });

  console.log(`\nSemantic Hybrid search results:`);
  for await (const answer of response.answers) {
    if (answer.highlights) {
      console.log(`Semantic answer: ${answer.highlights}`);
    } else {
      console.log(`Semantic answer: ${answer.text}`);
    }

    console.log(`Semantic answer score: ${answer.score}\n`);
  }

  for await (const result of response.results) {
    console.log(`Title: ${result.document.title}`);
    console.log(`Reranker Score: ${result.rerankerScore}`); // Reranker score is the semantic score
    console.log(`Content: ${result.document.content}`);
    console.log(`Category: ${result.document.category}`);

    if (result.captions) {
      const caption = result.captions[0];
      if (caption.highlights) {
        console.log(`Caption: ${caption.highlights}`);
      } else {
        console.log(`Caption: ${caption.text}`);
      }
    }

    console.log(`\n`);
  }
}

main();
