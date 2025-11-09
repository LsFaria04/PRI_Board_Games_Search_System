#!/bin/bash

# query solr and convert results to trec format
python3 ./evaluation_scripts/query_solr.py \
    --queries queries \
    --collection board_games | \

python3 ./evaluation_scripts/solr2trec.py > output/results_trec.txt

# run evaluation pipeline.
#THE QRELS FILE MUST BE CREATED MANUALLY!!!
./trec_eval/trec_eval \
    -q -m all_trec \
    qrels_trec.txt output/results_trec.txt | 
python3 ./evaluation_scripts/plot_pr.py

#Run the trec_eval again to create a file with the metrics
./trec_eval/trec_eval \
    -q -m all_trec \
    qrels_trec.txt output/results_trec.txt > output/trec_metrics.txt

# cleanup
rm output/results_trec.txt
