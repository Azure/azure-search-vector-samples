const dotenv = require("dotenv");
const fs = require("fs");
const { SearchIndexClient, SearchClient } = require("@azure/search-documents");
const { DefaultAzureCredential } = require("@azure/identity")
const { AzureKeyCredential } = require("@azure/core-auth")
const { OpenAIClient } = require("@azure/openai");
const { promisify } = require('util');
const { Option, program } = require('commander');


async function main() {
  program
    .option('-e, --embed', 'Recreate embeddings in text-sample.json')
    .option('-u, --upload', 'Upload embeddings and data in text-sample.json to the search index')
    .option('-q, --query <text>', 'Text of query to issue to search, if any')
    .addOption(new Option('-k, --query-kind <kind>', 'Kind of query to issue. Defaults to hybrid').default('hybrid').choices(['text', 'vector', 'hybrid']))
    .option('-c, --category-filter <category>', 'Category to filter results to')
    .option('-t, --include-title', 'Search over the title field as well as the content field')
    .option('--no-semantic-reranker', 'Do not use semantic reranker. Defaults to false')
    .parse();

  const options = program.opts()
  const defaultCredential = new DefaultAzureCredential();

  // Load environment variables from .env file
  dotenv.config({ path: "../.env" });

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
    // Create Azure AI Search index
    try {
      await createSearchIndex(defaultCredential);
    } catch (err) {
      console.error(`Failed to create index: ${err.message}`);
      return;
    }

    try {
      await uploadDocuments(defaultCredential);
    } catch (err) {
      console.error(
        `Failed to upload documents to search index: ${err.message}`
      );
      return;
    }
  }

  // Query Azure AI Search
  if (options.query) {
    try {
      await queryDocuments(defaultCredential, options.query, options.queryKind, options.categoryFilter, options.includeTitle, options.semanticReranker);
    } catch (err) {
      console.error(
        `Failed to issue query to search index: ${err.message}`
      );
      return;
    }
  }
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

function createOpenAiClient(defaultCredential) {
  const openAiEndpoint = process.env.AZURE_OPENAI_ENDPOINT;
  const openAiKey = process.env.AZURE_OPENAI_KEY;
  let credential = !openAiKey || openAiKey.trim() == '' ?
    defaultCredential : new AzureKeyCredential(openAiKey);
  return new OpenAIClient(openAiEndpoint, credential);
}


const readFileAsync = promisify(fs.readFile);
const writeFileAsync = promisify(fs.writeFile);

async function generateDocumentEmbeddings(defaultCredential) {
  console.log("Reading data/text-sample.json...");
  const fileData = await readFileAsync("../data/text-sample.json", "utf-8");
  let data = JSON.parse(fileData);

  console.log("Generating embeddings with Azure OpenAI...");
  const client = createOpenAiClient(defaultCredential);
  const openAiDeployment = process.env.AZURE_OPENAI_EMBEDDING_DEPLOYMENT;

  const titles = data.map(item => item["title"]);
  const content = data.map(item => item["content"]);
  const titleEmbeddings = await client.getEmbeddings(openAiDeployment, titles);
  const contentEmbeddings = await client.getEmbeddings(openAiDeployment, content);

  for (let i = 0; i < data.length; i++) {
    data[i]["titleVector"] = titleEmbeddings.data[i].embedding;
    data[i]["contentVector"] = contentEmbeddings.data[i].embedding;
  }

  await writeFileAsync("../data/text-sample.json", JSON.stringify(data, null, 2));
  console.log("Wrote embeddings to data/text-sample.json");
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

  console.log("Creating index...");
  await indexClient.createOrUpdateIndex(index);
}

async function uploadDocuments(defaultCredential) {
  console.log("Reading data/text-sample.json...");
  const fileData = await readFileAsync("../data/text-sample.json", "utf-8");
  let data = JSON.parse(fileData);

  const searchClient = createSearchClient(defaultCredential);

  console.log("Uploading documents to the index...");

  // Upload 1 document at a time
  for (let i = 0; i < data.length; i++) {
    await searchClient.uploadDocuments([data[i]]);
  }

  console.log("Finished uploading documents");
}

async function queryDocuments(defaultCredential, query, queryKind, categoryFilter, includeTitle, semanticReranker) {
  const searchClient = createSearchClient(defaultCredential);
  const openAiClient = createOpenAiClient(defaultCredential);
  const openAiDeployment = process.env.AZURE_OPENAI_EMBEDDING_DEPLOYMENT;

  let options = {
    select: ["title", "content", "category"],
    top: 3
  };

  if (queryKind == "vector" || queryKind == "hybrid") {
    let embeddingResponse = await openAiClient.getEmbeddings(openAiDeployment, [query]);
    let embedding = embeddingResponse.data[0].embedding;
    let vectorFields = includeTitle ? [ "contentVector", "titleVector" ] : [ "contentVector" ]; 
    options["vectorSearchOptions"] = {
      queries:  [
        {
          kind: "vector",
          vector: embedding,
          kNearestNeighborsCount: 50,
          fields: vectorFields
        }
      ]
    }
  }

  if (semanticReranker) {
    if (queryKind == "text" || queryKind == "hybrid") {
      options["queryType"] = "semantic";
    } else {
      options["semanticQuery"] = query;
    }

    options["semanticSearchOptions"] = {
      answers: {
        answerType: "extractive"
      },
      captions:{
          captionType: "extractive"
      },
      configurationName: "my-semantic-config",
    }
  }

  if (categoryFilter) {
    options["filter"] = `category eq '${categoryFilter}'`;
  }

  const searchText = queryKind == "text" || queryKind == "hybrid" ? query : "*";
  const response = await searchClient.search(searchText, options);

  if (semanticReranker) {
    for await (const answer of response.answers) {
      if (answer.highlights) {
        console.log(`Semantic answer: ${answer.highlights}`);
      } else {
        console.log(`Semantic answer: ${answer.text}`);
      }

      console.log(`Semantic answer score: ${answer.score}\n`);
    }
  }

  for await (const result of response.results) {
    console.log('----');
    console.log(`Title: ${result.document.title}`);
    console.log(`Score: ${result.score}`);
    if (semanticReranker) {
      console.log(`Reranker Score: ${result.rerankerScore}`); // Reranker score is the semantic score
    }
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

    console.log('----');
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
