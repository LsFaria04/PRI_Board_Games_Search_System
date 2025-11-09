#!/bin/bash

docker stop meic_solr
docker rm meic_solr

# This script expects a container started with the following command.
docker run -p 8983:8983 --name meic_solr -v ${PWD}:/data -d solr:9 solr-precreate board_games

docker cp synonyms.txt meic_solr:/var/solr/data/board_games/conf
sleep 3

docker cp stopwords.txt meic_solr:/var/solr/data/board_games/conf
sleep 3

# Load the schema
curl -X POST -H 'Content-type:application/json' \
    --data-binary "@./schema.json" \
    http://localhost:8983/solr/board_games/schema

# Populate collection using mapped path inside container.
docker exec -it meic_solr solr post -c board_games /data/final_data.json



