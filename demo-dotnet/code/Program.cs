using System.Reflection.Metadata;
using Microsoft.Extensions.Configuration;
using Newtonsoft.Json.Linq;
using System.Text;
using Newtonsoft.Json;
using System.IO;

namespace VectorSearch
{
    class Program
    {
		private static HttpClient client = new HttpClient();
		private static string serviceName = "";
		private static string indexName = "";
		private static string apiKey = "";
		private static string azureOpenAIKey = "";
		private static string embeddingModel = "";

        static async Task Main(string[] args)
        {
			var builder = new ConfigurationBuilder()
					.AddJsonFile($"local.settings.json", true, true);
			var config = builder.Build();
			serviceName = config["Search_Service_Name"];
			indexName = config["Search_Index_Name"];
			apiKey = config["Search_Admin_Key"];
			azureOpenAIKey = config["AzureOpenAIKey"];
			embeddingModel = config["EmbeddingModel"];
			

				   
            Console.WriteLine("Would you like to index content? (y/n) ");
			string answer = Console.ReadLine();
			if (answer == "y")
			{
				bool bSuccess = await IndexContent();
				if (bSuccess)
				{
					Console.WriteLine("Indexing complete");
				}
				else
				{
					Console.WriteLine("Indexing failed");
				}
			}
			else
			{
				Console.WriteLine("Enter your search query: ");
				string query = Console.ReadLine();

				Search search = new Search
				{
					Vector = new Vector
					{
						Value = await GetEmbeddings(query),
						Fields = "contentVector",
						K = 5
					},
					Select = "title,content"
				};

				var results = await Search(search);
				Console.WriteLine("Search results: ");
				foreach (var result in results)
				{
					Console.WriteLine(result.Title);
					Console.WriteLine(result.Content);
				}
			}
        }

		private static async Task<bool> IndexContent()
		{
			try
			{
				
				StreamReader sr = new StreamReader("../data/text-sample.json");
				//Read the first line of text
				string content = sr.ReadLine();
				//Continue to read until you reach end of file
				while (!sr.EndOfStream)
				{
					//write the line to console window
					// Console.WriteLine(content);
					//Read the next line
					content += sr.ReadLine();
				}
				//close the file
				sr.Close();

				var documents = JsonConvert.DeserializeObject<List<InputDoc>>(content);

				List<Document> searchDocuments = new List<Document>();
				foreach(var doc in documents)
				{
					Document documentToIndex = new Document();
					documentToIndex.ContentVector = await GetEmbeddings(doc.Content);
					documentToIndex.TitleVector = await GetEmbeddings(doc.Title);
					documentToIndex.Content = doc.Content;
					documentToIndex.Title = doc.Title;
					documentToIndex.Id = doc.Id.ToString();
					documentToIndex.SearchAction = "upload";
					searchDocuments.Add(documentToIndex);
				}
				await IndexDocument(searchDocuments);

				return true;
			}
			catch (Exception ex)
			{
				Console.WriteLine(ex.Message);
				return false;
			}
		}

		public static async Task<List<double>> GetEmbeddings(string text)
		{
			//clear out the default headers
			client.DefaultRequestHeaders.Clear();
			client.DefaultRequestHeaders.Add("api-key", azureOpenAIKey);
			
			// client.DefaultRequestHeaders.Add("Content-Type", "application/json");
			var requestMessage = new HttpRequestMessage(HttpMethod.Post, "https://adtestmsft.openai.azure.com/openai/deployments/" + embeddingModel + "/embeddings?api-version=2022-12-01");

			text = text.Replace("\n", " ");
			string json = JsonConvert.SerializeObject(new Dictionary<string, string> { { "input", text } });
			
			requestMessage.Content = new StringContent(json); //"{\"input\": \"" + text + "\"}");
			requestMessage.Content.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("application/json");
			var response = await client.SendAsync(requestMessage);
			
			
			var responseString = await response.Content.ReadAsStringAsync();
			// Console.WriteLine(responseString);
			Embedding embeddings = JsonConvert.DeserializeObject<Embedding>(responseString);
			//wait for 2 seconds to avoid throttling
			Thread.Sleep(2000);
			return embeddings.Data.FirstOrDefault().Embedding;
		}

		// Index a document in Cognitive Search
		public static async Task<string> IndexDocument(List<Document> documents)
		{
			//clear out the default headers
			client.DefaultRequestHeaders.Clear();
			client.DefaultRequestHeaders.Add("api-key", apiKey);
			// client.DefaultRequestHeaders.Add("Content-Type", "application/json");
			var requestMessage = new HttpRequestMessage(HttpMethod.Post,"https://" + serviceName + ".search.windows.net/indexes/" + indexName + "/docs/index?api-version=2023-07-01-Preview");
			string json = "{\"value\": " + JsonConvert.SerializeObject(documents) + "}";
			requestMessage.Content = new StringContent(json);
			requestMessage.Content.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("application/json");
			var response = await client.SendAsync(requestMessage);
			var responseString = await response.Content.ReadAsStringAsync();
			return responseString;
		}

		// Vector search
		public static async Task<List<Document>> Search(Search search, int top = 10)
		{
			//clear out the default headers
			client.DefaultRequestHeaders.Clear();
			client.DefaultRequestHeaders.Add("api-key", apiKey);
			// client.DefaultRequestHeaders.Add("Content-Type", "application/json");
			var requestMessage = new HttpRequestMessage(HttpMethod.Post, "https://" + serviceName + ".search.windows.net/indexes/" + indexName + "/docs/search?api-version=2023-07-01-Preview");
			// string json = "{\"vector\": {\"value\": " + JsonConvert.SerializeObject(vectors) + ", \"fields\": \"contentVector\", \"k\": 5 \"}, \"select\": \"title, content\"}";
			string json = JsonConvert.SerializeObject(search);
			requestMessage.Content = new StringContent(json);
			requestMessage.Content.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("application/json");
			var response = await client.SendAsync(requestMessage);
			var responseString = await response.Content.ReadAsStringAsync();
			var responseJson = JObject.Parse(responseString);
			Console.WriteLine(responseString);
			var results = responseJson["value"].ToObject<List<Document>>();
			return results;
		}

    }
}