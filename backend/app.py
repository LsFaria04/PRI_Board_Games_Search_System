from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
from pathlib import Path
import requests

# Add evaluation_scripts 
sys.path.append(str(Path(__file__).parent.parent / "evaluation_scripts"))
import query_embeddings

app = Flask(__name__)
CORS(app)

SOLR_ENDPOINT = "http://localhost:8983/solr"
SOLR_COLLECTION = "board_games"

@app.route('/api/search/semantic', methods=['POST'])
def semantic_search():
    """Semantic search using embeddings from query_embeddings.py"""
    try:
        data = request.json
        query_text = data.get('query', '')
        page = data.get("page", "")

        try:
            page = int(page)
        except ValueError:
            page = 0 #page is not a number
        
        if not query_text:
            return jsonify({'error': 'Query is required'}), 400
        
        # Use the text_to_embedding function from query_embeddings.py
        embedding = query_embeddings.text_to_embedding(query_text)
        
        # Use the solr_knn_query function from query_embeddings.py, maybe need to adjust to get more fields
        fields = "id,name,description,yearpublished,average,score"
        solr_data = query_embeddings.solr_knn_query(SOLR_ENDPOINT, SOLR_COLLECTION, embedding, page)
        
        # Extract results
        results = solr_data.get('response', {}).get('docs', [])
        numFound = solr_data.get('response', {}).get('numFound', "")
        
        return jsonify({'results': results, 'numFound': numFound}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search/keyword', methods=['POST'])
def keyword_search():
    """Keyword search using standard Solr queries, need to change the params"""
    try:
        data = request.json
        query = data.get('query', '')
        page = data.get("page", "")

        try:
            page = int(page)
        except ValueError:
            page = 0 #page is not a number

        
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Query Solr with keyword search
        url = f"{SOLR_ENDPOINT}/{SOLR_COLLECTION}/select"
        
        params = {
            'q': query,
            'fl': 'id,score,name,alt_names,yearpublished,description,minplayers,maxplayers,playingtime,minage,publishers,designers,artists,categories,mechanics,families,expansions,average,owned,trading,wanting,wishing,averageweight',
            'rows': 9,
            'start': page * 9,
            'wt': 'json',
            'defType': 'edismax',
            "q.op": "AND",
            "qf": "name^5 alt_names^2 description^4 categories^4 mechanics^4 publishers^4 designers^3 artists^1 families^2 expansions^2 minage_str^3 yearpublished_str^3 playingtime_str^3 minplayers_str^3",
            "pf": "name^4 description^2 alt_names^2 publishers^4 designers^2 artists^2 categories^4 mechanics^4 families^2",
            "bf": "recip(bayesaverage,1,10,10)^3 recip(owned,1,1000,1000)^1 recip(trading,1,1000,1000)^1 recip(wanting,1,1000,1000)^1 recip(wishing,1,1000,1000)^3",
            "ps" : 2,
            "sort": "score desc",
        }
        
        response = requests.post(url, data=params)
        solr_data = response.json()
        
        results = solr_data.get('response', {}).get('docs', [])
        numFound = solr_data.get('response', {}).get('numFound', "")
        
        return jsonify({'results': results, 'numFound': numFound}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
