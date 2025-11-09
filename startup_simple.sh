#!/bin/bash

docker stop meic_solr
docker rm meic_solr

# This script expects a container started with the following command.
docker run -p 8983:8983 --name meic_solr -v ${PWD}:/data -d solr:9 solr-precreate board_games

# Populate collection using mapped path inside container.
docker exec -it meic_solr solr post -c board_games /data/final_data.json



