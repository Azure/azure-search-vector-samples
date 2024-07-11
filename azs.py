import json
import string
import requests
import pandas as pd
import numpy as np
from jsonpath_ng import jsonpath, parse
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from io import StringIO
# from evaluation import evaluate
from datasets import load_dataset
from mteb.evaluation.evaluators import RetrievalEvaluator
import mlflow
from collections import defaultdict
from dotenv import load_dotenv
import os




key_vault_url = "https://tidickerson-kv.vault.azure.net/"
secret_name = "apikey"


credential = DefaultAzureCredential()



class AzureSearch:
    def __init__(self, endpoint, api_key, api_version, service, query_payload =None, vectorizer=None):
        self.endpoint = endpoint
        self.api_key = api_key
        self.api_version = api_version
        self.service_name = service
        self.base_url = f"https://{self.service_name}.search.windows.net"

        self.headers = {
            'Content-Type' : 'application/json',
            'api-key':self.api_key
        }
        self.query_payload = query_payload
        self.vectorizer = vectorizer
    
    def url(self,path):
        return f"{self.base_url}/{path}?api-version={self.api_version}"
    
    def create_index(self,name,data=None):
        # if data is None:
        #     data = {
        #         "name":name,
        #         "fields": self.create_fields(),
        #         "vectorSearch": self.create_profiles()
        #     }
        
        response = requests.put(self.url(f'indexes/{name}'), json = data, headers=self.headers, verify=False)

        return response.json()

    def index(self, index, documents):
        for d in documents:
            print(d)
            if '_id' in d:
                d['_id'] = d.pop('_id')
            d['@search.action'] = "mergeOrUpload"
        data = {"value":documents}
        response = requests.post(self.url(f'indexes/{index}/docs/index'), json=data, headers=self.headers, verify=False)
        return response.json()
    
    def search(self, index, q):
        headers = {
            'Content-Type': 'application/json',
            'api-key': api_key  # Ensure api_key is defined or passed correctly
        }
        params = {
            'api-version': api_version  # Ensure api_version is defined or passed correctly
        }
        url = f"https://{service_name}.search.windows.net/indexes/{index}/docs/search"

        try:
            response = requests.post(url, json=q, headers=headers, params=params)
            response.raise_for_status()  # Raise an HTTPError for bad status codes

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Unexpected status code: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Error requesting data: {e}")
            return None




            
    def create_fields(self,dimension=1024,profile="hnsw"):
        fields = [
            {
                "name": "id",
                "type": "Edm.String",
                "key": True,
                "searchable": True
            },
            {
                "name": "title",
                "type": "Edm.String",
                "searchable": True,
                "analyzer": "standard.lucene",
                "filterable": "false",
                "retrievable": True,
                "sortable": False,
                "facetable": False
            },
            {
                "name": "text",
                "type": "Edm.String",
                "searchable": True,
                "analyzer": "standard.lucene",
                "filterable": "false",
                "retrievable": True,
                "sortable": False,
                "facetable": False
            },
            {
                "name": "cohere_embedding_binary",
                "type": "Collection(Edm.Byte)",
                "vectorEncoding": "packedBit",
                "dimensions": dimension,
                "searchable": True,
                "retrievable": True,
                "filterable": False,
                "facetable": False,
                "sortable": False,
                "vectorSearchProfile": "binaryhnsw"
            },
            {
                "name": "cohere_embedding_float",
                "type": "Collection(Edm.Single)",
                "dimensions": dimension,
                "searchable": True,
                "retrievable": True,
                "filterable": False,
                "facetable": False,
                "sortable": False,
                "vectorSearchProfile": profile
            }
        ]
        return fields
    
    def create_profiles(self,metric='cosine'):
        vector_search = {
                "profiles": [
                    {
                        "name": "eknn",
                        "algorithm": "exhaustive"
                    },
                    {
                        "name": "hnsw",
                        "algorithm": "defaulthnsw"
                    },
                    {
                        "name": "binaryhnsw",
                        "algorithm": "binaryhnsw"
                    },
                    {
                        "name": "hnswsq",
                        "compression": "mysq",
                        "algorithm": "defaulthnsw"
                    }
                ],
                "compressions": [
                    {
                        "name": "mysq",
                        "kind": "scalarQuantization",
                        "rerankWithOriginalVectors": True,
                        "defaultOversampling": 2,
                        "scalarQuantizationParameters": { 
                            "quantizedDataType": "int8"
                        } 
                    }
                ],
                "algorithms": [
                    {
                        "name": "exhaustive",
                        "kind": "exhaustiveKnn",
                        "exhaustiveKnnParameters": {
                            "metric": metric
                        }
                    },      
                    {
                        "name": "defaulthnsw",
                        "kind": "hnsw",
                        "hnswParameters": {
                            "m": 4,
                            "efConstruction": 400,
                            "metric": metric
                        }
                    },
                    {
                        "name": "binaryhnsw",
                        "kind": "hnsw",
                        "hnswParameters": {
                            "m": 4,
                            "efConstruction": 400,
                            "metric": "hamming"
                        }
                    }
                ]
            }
        return vector_search
    
    def set_vectorizer(self, vectorizer_model):
        self.vectorizer = vectorizer_model
    
    def vectorize(self,text,embedding_type):
        if self.vectorizer is None:
            raise Exception("Vectorizer not set")
        return self.vectorizer.embed(text,embedding_type)

    def get_search_results(self, queries, index_name):
        results = {}
        for qid in queries.keys():
            #skip processed queries
            if qid in results:
                continue
            #retrieve the query and run search 
            q = queries[qid]
            r = self.search(index_name, q)
            try:
                #extract the id and search score and store the score in results with the id as key
                results[qid] = {item['document_id']: item['@search.score'] for item in r['value']}
            except:
                # print(r)
                raise
        return results


        

def batch_dataframe(df, batch_size=100):
    total_rows = len(df)
    for start in range(0, total_rows, batch_size):
        end = min(start+batch_size,total_rows)
        yield df.iloc[start:end]
    
def create_index(endpoint, key, version, service, name, output, data=None, dimensions=None):
    secret = secret_client.get_secret(key).value

    ss = AzureSearch(endpoint,key,version,service)
    if data is not None:
        with open(data,'r') as f:
            data = json.load(f)
    
    if dimensions is not None:
        for field in data['fields']:
            if 'dimensions' in field:
                field['dimension'] = dimensions
    
    json_path_expr = parse('$.name')
    for match in json_path_expr.find(data):
        match.full_path.update(data,name)
    
    r = ss.create_index(name,data=data)
    with open(output,'w') as f:
        f.write(json.dumps(r))
    return r

def convert_ndarray_to_list(value):
    if isinstance(value,np.ndarray):
        return value.tolist()
    return value

def select_and_rename_columns(df,columns):
    if isinstance(columns,list):
        new_df = df[columns]
    elif isinstance(columns,dict):
        new_df = pd.DataFrame()
        for key,value in columns.items():
            if isinstance(value,list):
                for v in value:
                    new_df[v] = df[key]
            else:
                new_df[value] = df[key]
    else:
        raise ValueError("Columns must either be a list or dicitonary")
    return new_df

def index_data(endpoint, key, version, service, index, data, output, columns=None):
    df = pd.read_feather(data)
    df = df.applymap(convert_ndarray_to_list)
    # df = select_and_rename_columns(df,columns)
    # print(df.columns)

    ss = AzureSearch(endpoint,key,version,service)

    for batch in batch_dataframe(df):
        data = batch.to_dict(orient='records')
        r = ss.index(index, data)
        print(r)
    
    print("Indexed %d data successfully"%len(df))
    with open(output,'w') as f:
        f.write("Indexed %d data successfully"%len(df))
    
def search_advanced(endpoint, key, version, service, index, query_payload, result_file):
    # Assuming query_payload is the path to the JSON file
    df_queries = pd.read_json('query_payload_file.json')

    # Expand the 'requests' column into separate columns
    df_expanded = pd.json_normalize(df_queries['requests'])

    # Set 'document_id' as the index
    dict_expanded = df_expanded.set_index('document_id').to_dict(orient='index')

    # Create an instance of AzureSearch
    ss = AzureSearch(endpoint, key, version, service)

    # Get search results
    results = ss.get_search_results(dict_expanded, index)

    # Write the results to the result file
    with open(result_file, 'w') as f:
        json.dump(results, f, indent=4)


def search(endpoint, key, version, service, index, query_file, vector_column, field, k, result_file, oversampling=None):
    #read feather file to a data frame
    df_queries = pd.read_feather(query_file)
    #convert the numpy arrays to lists
    df_queries[vector_column] = df_queries[vector_column].map(lambda x: x.tolist())
    #convert df to dictionary
    queries = df_queries.set_index('_id').to_dict(orient='index')

    #constructs the payload based on if oversampling is None or not, conditional based on oversampling since it is an optional param
    if oversampling is None:
        query_payload = """{{
                "select": "id",
                "vectorQueries": [{{
                    "kind": "vector",
                    "vector": {%s},
                    "fields": "%s",
                    "k":%d
                }}]
            }}""" % (vector_column, field, k)
    else:
        query_payload = """{{
                "select": "id",
                "vectorQueries": [{{
                    "kind": "vector",
                    "vector": {%s},
                    "fields": "%s",
                    "k":%d,
                    "oversampling": %f
                }}]
            }}""" % (vector_column, field, k, oversampling)

    #same function as in advanced search

    ss = AzureSearch(endpoint, key, version, service, query_payload=query_payload)
    r = ss.get_search_results(queries, index)

    with open(result_file, 'w') as f:
        f.write(json.dumps(r, indent=4))


#assesses the performance of retrieval models, determining how well they retrieve and rank relevant item
evaluator = RetrievalEvaluator()

#all of the data sets in a list
mteb_datasets = [
    "mteb/arguana", "mteb/climate-fever", "mteb/cqadupstack-android", "mteb/cqadupstack-english",
    "mteb/cqadupstack-gaming", "mteb/cqadupstack-gis", "mteb/cqadupstack-mathematica", "mteb/cqadupstack-physics",
    "mteb/cqadupstack-programmers", "mteb/cqadupstack-stats", "mteb/cqadupstack-tex", "mteb/cqadupstack-unix",
    "mteb/cqadupstack-webmasters", "mteb/cqadupstack-wordpress", "mteb/dbpedia", "mteb/fever", "mteb/fiqa",
    "mteb/hotpotqa", "mteb/msmarco", "mteb/nfcorpus", "mteb/nq", "mteb/quora", "mteb/scidocs", "mteb/scifact",
    "mteb/touche2020", "mteb/trec-covid"
]

#get rid of mteb/ in all of the datasets
s = "mteb/scidocs"
mteb_name_set = set(s.replace("mteb/", ""))

#function takes in arels and makes a qrel dict
def get_labels(qrels):
    qrels_dict = defaultdict(dict)
    #maps the score to the query id and corpus id
    def qrels_dict_init(row):
        qrels_dict[row["query-id"]][row["corpus-id"]] = int(row["score"])
    
    #then if test or dev keys exist in the input, apply qrels_dict_init function
    if 'test' in qrels:
        qrels['test'].map(qrels_dict_init)
        
    if 'dev' in qrels:
        qrels['dev'].map(qrels_dict_init)
    return qrels_dict

#remove labels not in the corpus ids set
def clean_labels(qrels_dict, corpus_ids):
    corpus_ids_set = set(corpus_ids)
    for q in qrels_dict:
        ds = list(qrels_dict[q].keys())
        for d in ds:
            if not d in corpus_ids_set:
                qrels_dict[q].pop(d)
    return qrels_dict


#create new kv pair filtered dict that only includes values from result if they are in qrels_dict
def clean_result(qrels_dict, result):
    filtered_dict = {k: result[k] for k in qrels_dict if k in result}
    # print("Filtered Dictionary:", filtered_dict)
    return filtered_dict

def write_results_to_json(results, output_filename):
    with open(output_filename, 'w') as json_file:
        json.dump(results, json_file, indent=4)
    print(f'Results have been written to {output_filename}')


#the big one
def evaluate(result_file, output, dataset_name=None, qrel_path=None, corpus_ids=None):
    #if there is a dataset name print a message for it
    if dataset_name:
        print("loading dataset: %s" % dataset_name)
        #if it is in the mteb_name_set, add mteb/ back to it
        if dataset_name in mteb_name_set:
            dataset_name = "mteb/" + dataset_name
        #load the dataset for ML and NLP tasks
        qrels = load_dataset(dataset_name, 'default')
    #else if we get a qrel file path, load that instead
    elif qrel_path:
        print("loading qrel file: %s" % qrel_path)
        qrels = load_dataset(qrel_path)
    else:
        raise ValueError("Dataset name or path to qrel file must be provided")
    
    #read and parse result_file, assign to results
    results = json.load(open(result_file))

    #assign the labels from qrels to qrels_dict
    qrels_dict = get_labels(qrels)
    write_results_to_json(qrels_dict,'qrels_dict.json')
    #if the corpus_ids arent null, assign the cleaned labels to the qrels dict
    if corpus_ids is not None:
        qrels_dict = clean_labels(qrels_dict, corpus_ids)
    
    #get the cleaned results
    results = clean_result(qrels_dict, results)
    write_results_to_json(results,'cleaned_labels.json')
    evaluation_results = evaluator.evaluate(qrels_dict, results, [1, 5, 10])
    ndcg = evaluation_results[0]
    _map = evaluation_results[1]
    recall = evaluation_results[2]
    precision = evaluation_results[3]
    

    # Print the extracted values
    print(ndcg)
    print(_map)
    print(recall)
    print(precision)

    

if __name__ == "__main__":
    endpoint = "https://tidickerson2"
    api_version = '2024-05-01-preview'
    service_name = "tidickerson2"
    index_name = "test-index1"
    self_base = f"https://{service_name}.search.windows.net"
    index_definition = 'index_def.json'
    query_payload_file = 'query_payload.json'
    result_file = 'output.json'
    
    client = SecretClient(vault_url=key_vault_url, credential=credential)
    retrieved_secret = client.get_secret(secret_name)
    api_key = retrieved_secret.value






    #import the dataset from metb-corpus, loads in

  

    

    # #initialize the service

    azure_search = AzureSearch(endpoint,api_key,api_version,service_name)


    

    
    # with open(index_definition,'r') as f:
    #     index_definition = json.load(f)

    # # print(index_definition)

    # # #create the index
    
    # # #index is able to be successfully created from json file
    
    # create_index_response = azure_search.create_index(index_name, index_definition)
    # print("Create Index Response:", create_index_response)
    
   

    # # # #index documents

    # # Define the file path
    # #able to index documents based on filepath if in same directory
    # """
    # converted loaded in dataset, converted df to feather file, renamed all of the columns to match the index definition, and indexed the data successfully
    # """

    # df = pd.read_json("hf://datasets/mteb/scidocs/corpus.jsonl", lines=True)
    # new_column_names = {
    #     '_id': 'document_id',
    #     'title':'title',
    #     'text': 'content'
    # }
    # new_df = select_and_rename_columns(df,new_column_names)
    # new_df.to_feather('input.feather')
    # print("DataFrame Columns:", df.columns)

    
    # index_data(endpoint, api_key, api_version, service_name, index_name, 'input.feather','output.txt')

        
    # """
    # POST INDEX CREATION AND DOCUMENT INDEXING
    # """
   

    search_advanced(endpoint, api_key, api_version, service_name, index_name, r'C:\Users\t-idickerson\project\query_payload_file.json', result_file)

    # # #evaluate the search results

    evaluate('output.json', 'result_file.txt', dataset_name="mteb/scidocs", qrel_path=None, corpus_ids=None)
    


   

   



    