namespace VectorSearch
{
    using System;
    using System.Collections.Generic;

    using System.Globalization;
	using Newtonsoft.Json;
    using Newtonsoft.Json.Converters;

    public class Document
    {
		[JsonProperty("id")]
		public string Id { get; set; }
		[JsonProperty("title")]
		public string Title { get; set; }
		[JsonProperty("content")]
		public string Content { get; set; }
		[JsonProperty("contentVector")]
		public List<double> ContentVector { get; set; }
		[JsonProperty("titleVector")]
		public List<double> TitleVector { get; set; }
		[JsonProperty("@search.action")]
		public string SearchAction { get; set; }
	}
}