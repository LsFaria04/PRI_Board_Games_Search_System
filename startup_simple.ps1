# Stop and remove existing container
docker stop meic_solr
docker rm meic_solr

# Get current directory in Docker-compatible format
$pwd = (Get-Location).Path -replace '\\', '/'
$dockerPath = "/$($pwd -replace ':', '')"

# Run Solr container with volume mount
docker run -p 8983:8983 --name meic_solr -v "${dockerPath}:/data" -d solr:9 solr-precreate board_games

# Wait for container to initialize
Start-Sleep -Seconds 20

# Post data to Solr
docker exec -it meic_solr solr post -c board_games /data/final_data.json
