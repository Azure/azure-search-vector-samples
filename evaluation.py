from collections import defaultdict
from datasets import load_dataset
from mteb.evaluation.evaluators import RetrievalEvaluator
import fire
from mteb.evaluation.evaluators import RetrievalEvaluator
import mlflow

#assesses the performance of retrieval models, determining how well they retrieve and rank relevant item
evaluator = RetrievalEvaluator()

#all of the data sets in a list
# mteb_datasets = [
#     "mteb/arguana", "mteb/climate-fever", "mteb/cqadupstack-android", "mteb/cqadupstack-english",
#     "mteb/cqadupstack-gaming", "mteb/cqadupstack-gis", "mteb/cqadupstack-mathematica", "mteb/cqadupstack-physics",
#     "mteb/cqadupstack-programmers", "mteb/cqadupstack-stats", "mteb/cqadupstack-tex", "mteb/cqadupstack-unix",
#     "mteb/cqadupstack-webmasters", "mteb/cqadupstack-wordpress", "mteb/dbpedia", "mteb/fever", "mteb/fiqa",
#     "mteb/hotpotqa", "mteb/msmarco", "mteb/nfcorpus", "mteb/nq", "mteb/quora", "mteb/scidocs", "mteb/scifact",
#     "mteb/touche2020", "mteb/trec-covid"
# ]

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
    return filtered_dict

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
    #if the corpus_ids arent null, assign the cleaned labels to the qrels dict
    if corpus_ids is not None:
        qrels_dict = clean_labels(qrels_dict, corpus_ids)
    
    #get the cleaned results
    results = clean_result(qrels_dict, results)

    #assign the values from evaluate() to corresponding variables
    #1,5,10, probably refers to top 1,5,10 results
    ndcg, _map, recall, precision = evaluator.evaluate(qrels_dict, results, [1, 5, 10])

    #log the metric with ML Flow
    mlflow.log_metric("ndcg@10", ndcg['NDCG@10'])
    #write the values of the variables from evaluate to the output file, return ndcg score 
    with open(output, 'w') as f:
        f.write(f"ndcg: {ndcg}, map: {_map}, recall: {recall}, precision: {precision}")
    return ndcg


if __name__ == "__main__":
    evaluate('output.txt', 'result_file.txt', dataset_name='mteb/scidocs', qrel_path=None, corpus_ids=None)
