#!/bin/bash

#Create a query with embeddings
python3 ./evaluation_scripts/query_embeddings.py

# query solr and convert results to trec format
python3 ./evaluation_scripts/query_solr.py \
    --queries queries \
    --collection board_games > output/results.json