#!/bin/bash

# query solr and convert results to trec format
python3 ./evaluation_scripts/query_solr.py \
    --queries queries \
    --collection board_games > ../output/results.json