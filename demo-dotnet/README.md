## Getting Started
This is a sample app that shows how to index and documents with Vector Search.  This example uses Azure OpenAI's `text-embedding-ada-002 (Version 2)` model to vectorize the content.

In order to run this sample, you will need to create a `local.settings.json` file in the `code` folder with the following contents (provide your own values):

```
{
	"AzureOpenAIKey": "",

	"EmbeddingModel": "",

	"Search_Service_Name": "",

	"Search_Index_Name": "",

	"Search_Admin_Key": ""
}
```

After creating this file, you can run the app by issuing the `dotnet run` command from the terminal in the folder containing the `code.csproj` file.