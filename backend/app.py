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
        
        if not query_text:
            return jsonify({'error': 'Query is required'}), 400
        
        # Use the text_to_embedding function from query_embeddings.py
        embedding = query_embeddings.text_to_embedding(query_text)
        
        # Use the solr_knn_query function from query_embeddings.py, maybe need to adjust to get more fields
        fields = "id,name,description,yearpublished,average,score"
        solr_data = query_embeddings.solr_knn_query(SOLR_ENDPOINT, SOLR_COLLECTION, embedding)
        
        # Extract results
        results = solr_data.get('response', {}).get('docs', [])
        
        return jsonify({'results': results}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search/keyword', methods=['POST'])
def keyword_search():
    """Keyword search using standard Solr queries, need to change the params"""
    try:
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Query Solr with keyword search
        url = f"{SOLR_ENDPOINT}/{SOLR_COLLECTION}/select"
        
        params = {
            'q': query,
            'fl': 'id,name,description,yearpublished,average,score',
            'rows': 10,
            'wt': 'json',
            'defType': 'edismax',
            'qf': 'name alt_names description categories mechanics publishers'
        }
        
        response = requests.post(url, data=params)
        solr_data = response.json()
        
        results = solr_data.get('response', {}).get('docs', [])
        
        return jsonify({'results': results}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
