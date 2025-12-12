# Query solr and convert results to JSON format
python evaluation_scripts/query_solr.py --queries queries --collection board_games > output/results.json

# Generate qrels template from results
$json = Get-Content output/results.json | ConvertFrom-Json
$qrelsLines = @()
foreach ($queryId in $json.PSObject.Properties.Name) {
    foreach ($doc in $json.$queryId.response.docs) {
        $qrelsLines += "$queryId 0 $($doc.id)"
    }
}
$qrelsLines | Out-File -FilePath qrels_trec.txt -Encoding ASCII

Write-Host "Results saved to output/results.json"
Write-Host "qrels_trec.txt template created - add 0 or 1 at the end of each line for relevance"
