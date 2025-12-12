# Query solr and convert results to trec format (uses existing query file from half script)
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
$results = python evaluation_scripts/query_solr.py --queries queries --collection board_games | python evaluation_scripts/solr2trec.py
[System.IO.File]::WriteAllLines("$PWD/output/results_trec.txt", $results, $utf8NoBom)

# Run evaluation pipeline
# THE QRELS FILE MUST BE CREATED MANUALLY!!!
wsl ./trec_eval/trec_eval -q -m all_trec qrels_trec.txt output/results_trec.txt | python evaluation_scripts/plot_pr.py

# Run trec_eval again to create a file with the metrics
wsl ./trec_eval/trec_eval -q -m all_trec qrels_trec.txt output/results_trec.txt | Out-File -Encoding ASCII output\trec_metrics.txt

Write-Host "Evaluation complete!"
Write-Host "Metrics saved to output\trec_metrics.txt"
Write-Host "Plot saved to output\plot.png"
