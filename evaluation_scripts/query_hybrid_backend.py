import os
import json
import requests
import glob

# Configuration
QUERIES_DIR = "queries"  # Change if your hybrid queries are in a different folder
BACKEND_URL = "http://localhost:5000/api/search/hybrid"  # Change if your backend runs elsewhere
OUTPUT_PATH = "output/results.json"

all_results = {}

# Find all query files (1.json, 2.json, ...)
query_files = sorted(glob.glob(os.path.join(QUERIES_DIR, "*.json")))

for qf in query_files:
    with open(qf, "r", encoding="utf-8") as f:
        query_obj = json.load(f)
    # Use filename (without .json) as query id
    query_id = os.path.splitext(os.path.basename(qf))[0]
    try:
        resp = requests.post(BACKEND_URL, json=query_obj)
        resp.raise_for_status()
        data = resp.json()
        all_results[query_id] = {"response": {"docs": data.get("results", [])}}
    except Exception as e:
        all_results[query_id] = {"error": str(e)}

# Save results in the same format as other evaluation scripts
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(all_results, f, indent=2, ensure_ascii=False)

print(f"Saved hybrid search results to {OUTPUT_PATH}")
