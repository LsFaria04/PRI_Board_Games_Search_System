import requests
import json
from sentence_transformers import SentenceTransformer

def text_to_embedding(text):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embedding = model.encode(text, convert_to_tensor=False).tolist()
    
    # Convert the embedding to the expected format
    embedding_str = "[" + ",".join(map(str, embedding)) + "]"
    return embedding_str

#Used for the frontend
def solr_knn_query(endpoint, collection, embedding, page):
    url = f"{endpoint}/{collection}/select"

    data = {
        "q": f"{{!knn f=combined_vector topK=100}}{embedding}",
        "fl": "id,score,name,alt_names,yearpublished,description,minplayers,maxplayers,playingtime,minage,publishers,designers,artists,categories,mechanics,families,expansions,average,owned,trading,wanting,wishing,averageweight",
        "rows":9,
        "start": page * 9,
        "wt": "json",
        
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    response = requests.post(url, data=data, headers=headers)
    response.raise_for_status()
    return response.json()

def solr_hybrid_query(endpoint, collection, query, embedding, page):
    url = f"{endpoint}/{collection}/select"

    params = {
        'q': query,
        'fl': 'id,score,name,alt_names,yearpublished,description,minplayers,maxplayers,playingtime,minage,publishers,designers,artists,categories,mechanics,families,expansions,average,owned,trading,wanting,wishing,averageweight',
        #'rows': 9,
        'rows': 30, #to do evaluation with trec eval
        'start': page * 9,
        'wt': 'json',

        # Lexical search
        'defType': 'edismax',
        "q.op": "AND",
        "qf": "name^5 alt_names^2 description^4 categories^4 mechanics^4 publishers^4 designers^3 artists^1 families^2 expansions^2 minage_str^3 yearpublished_str^3 playingtime_str^3 minplayers_str^3",
        "pf": "name^4 description^2 alt_names^2 publishers^4 designers^2 artists^2 categories^4 mechanics^4 families^2",
        "bf": "recip(bayesaverage,1,10,10)^3 recip(owned,1,1000,1000)^1 recip(trading,1,1000,1000)^1 recip(wanting,1,1000,1000)^1 recip(wishing,1,1000,1000)^3",
        "ps": 2,

        #Semantic
        "knn": {
            "field": "combined_vector",
            "vector": embedding,
            "k": 100
        },


         # Sub-query aliases
        "lexicalQuery": f"{{!edismax q.op=AND qf='name^5 alt_names^2 description^4 categories^4 mechanics^4 publishers^4 designers^3 artists^1 families^2 expansions^2'}}({query})",
        "vectorQuery": f"{{!knn f=combined_vector topK={100}}}{embedding}",

        #Sort by the sum of the lexical and vector query (normalize the lexical)
        "sort": (
            "{!func}"
            "sum(product(0.3,scale(query($lexicalQuery),0,1)),product(0.7,query($vectorQuery))) desc"
        ),


    }

    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    response = requests.post(url, data=params, headers=headers)
    response.raise_for_status()
    return response.json()

#Used for the evaluation process. Creates a query file using the embeddings
def solr_knn_query_json(embedding):

    data = {
        "q": f"{{!knn f=combined_vector topK=100}}{embedding}",
        "fl": "id,score,name,alt_names,yearpublished,description,minplayers,maxplayers,playingtime,minage,publishers,designers,artists,categories,mechanics,families,expansions,average,owned,trading,wanting,wishing,averageweight",
        "rows":30,
        "wt": "json"
    }

    params = {
        "params": data
    }

    with open("queries/1.json", "w") as f:
        json.dump(params, f, indent=2)
    
                      

def display_results(results):
    docs = results.get("response", {}).get("docs", [])
    if not docs:
        print("No results found.")
        return

    for doc in docs:
        print(f"* {doc.get('id')} {doc.get('name')} [score: {doc.get('score'):.2f}]")

def main():
    #solr_endpoint = "http://localhost:8983/solr"
    #collection = "board_games"
    
    query_text = input("Enter your query: ")
    embedding = text_to_embedding(query_text)

    try:
        solr_knn_query_json(embedding)
    except requests.HTTPError as e:
        print(f"Error {e.response.status_code}: {e.response.text}")

if __name__ == "__main__":
    main()
