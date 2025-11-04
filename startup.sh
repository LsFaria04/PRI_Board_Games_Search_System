#!/bin/bash

# This script expects a container started with the following command.
#docker run -p 8983:8983 --name meic_solr -v ${PWD}:/data -d solr:9 solr-precreate board_games

# Schema definition via API
curl -X POST -H 'Content-type:application/json' \
    --data-binary "@./final_data.json" \
    http://localhost:8983/solr/board_games/update?commit=true


# Load the updated schema
curl -X POST -H 'Content-type:application/json' \
    --data-binary "@./schema.json" \
    http://localhost:8983/solr/board_games/schema

# Populate collection using mapped path inside container.
docker exec -it meic_solr solr post -c board_games /data/meic_courses.json



