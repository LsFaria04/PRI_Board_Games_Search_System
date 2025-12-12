#Create a query with embeddings
python evaluation_scripts/query_embeddings.py

# query solr and convert results to trec format
python evaluation_scripts/query_solr.py --queries queries --collection board_games > output/results.json

Write-Host "Results saved to output/results.json"
Write-Host "Next step: Review results and update qrels_trec.txt with relevance judgments"
