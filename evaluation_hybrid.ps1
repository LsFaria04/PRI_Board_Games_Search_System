
# Hybrid evaluation: run search, convert to TREC, and evaluate
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
$results = Get-Content output/results.json | python evaluation_scripts/solr2trec.py
[System.IO.File]::WriteAllLines("$PWD/output/results_trec.txt", $results, $utf8NoBom)

# Run evaluation pipeline
wsl ./trec_eval/trec_eval -q -m all_trec qrels_trec.txt output/results_trec.txt | python evaluation_scripts/plot_pr.py

# Save metrics
wsl ./trec_eval/trec_eval -q -m all_trec qrels_trec.txt output/results_trec.txt | Out-File -Encoding ASCII output\trec_metrics.txt

Write-Host "Evaluation complete!"
Write-Host "Metrics saved to output\trec_metrics.txt"
Write-Host "Plot saved to output\plot.png"
