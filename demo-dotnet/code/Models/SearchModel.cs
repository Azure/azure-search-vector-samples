namespace VectorSearch
{
    using System;
    using System.Collections.Generic;

    using System.Globalization;
	using Newtonsoft.Json;
    using Newtonsoft.Json.Converters;

    public class Search
    {
		[JsonProperty("vector")]
		public Vector Vector { get; set; }
		[JsonProperty("select")]
		public string Select { get; set; }
		
	}

	public class Vector
	{
		[JsonProperty("value")]
		public List<double> Value { get; set; }
		[JsonProperty("fields")]
		public string Fields { get; set; }
		[JsonProperty("k")]
		public int K { get; set; }

	}
}