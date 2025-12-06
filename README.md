# Board games search engine

## Development

To start evaluation process of the queries you need to follow these steps:
 - Initialize the solr containers using one of the scripts in the startup_scripts folder (.ps1 files are for Windows)
 - If you are working in Windows, open wsl in the working directory (just enter 'wsl' in the vscode terminal)
 - Use the following commands if you are using wsl:
    
    ```shell
        python3 -m venv prienv #Instantiate a new dev environment
        source prienv/bin/activate #Activates the environment 
    ```
- Use the following command to install the needed packages:
    ```shell
    pip install matplotlib numpy pandas scikit-learn requests pytrec_eval==0.5 #installs the packages needed to run the scripts
    ```
- For usage of trec_eval, run the following commands before running any script files:
    ```shell
    git clone https://github.com/usnistgov/trec_eval.git trec_eval
	cd trec_eval && make
	cd ..
    ```
- If you don't have the file qrels_trec.txt updated:
    - Run ./evaluation_half.sh to run the first half of the evaluation pipeline
    - Analyze the results in the file results.json and create a qrels.txt

- If you have problems still running the evaluation scripts in wsl, run these commands in powershell:
    -wsl bash -c "cd /mnt/c/Users/Utilizador/OneDrive/Ambiente\ de\ Trabalho/MEIC/PRI/BoardGamesEngine && sed -i 's/\r$//' evaluation.sh evaluation_half.sh"
    -wsl bash -c "cd /mnt/c/Users/Utilizador/OneDrive/Ambiente\ de\ Trabalho/MEIC/PRI/BoardGamesEngine && chmod +x evaluation.sh evaluation_half.sh"

- Run ./evaluation.sh to run the evaluation pipeline

- For semantic search, install the following python package (more informaton will be added regarding semantic search):
    ```shell
    pip install sentence-transformers
    ```


All queries are stored in the queries folder. To add a new query, simply place a JSON file in this directory and name it using an integer (e.g., 0001.json, 0002.json). This numeric naming determines the execution order when running the evaluation scripts.

The qrels_trec.txt file must be created manually. It contains the relevance judgments for each query, indicating whether a document is relevant (1) or not (0). The easiest way to generate candidates for labeling is to run the evaluation_half script, which executes the first half of the full evaluation pipeline and produces a file with the raw query results. You can then inspect these results to assign relevance labels accordingly.

## For the semantic_games.zip

After extracting the zip, there might be a mismatch between the encoding of the file and the encoding needed for Solr. To fix this, run these commands in WSL/Ubuntu:

```shell
# 1. Convert from UTF-16 to UTF-8
iconv -f UTF-16LE -t UTF-8 semantic_games.json > semantic_games_utf8.json
mv semantic_games_utf8.json semantic_games.json

# 2. Remove BOM (Byte Order Mark)
tail -c +4 semantic_games.json > semantic_games_fixed.json && mv semantic_games_fixed.json semantic_games.json

# 3. Rename combined_vectors to combined_vector
sed -i "s/combined_vectors/combined_vector/g" semantic_games.json
```

After running these commands, update your `startup_semantic.ps1` to post `semantic_games.json` instead of `final_data.json` in the data indexing step.