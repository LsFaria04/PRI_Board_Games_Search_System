import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
import pandas as pd

def get_stop_words(df):
    # Download resources
    nltk.download('punkt')
    nltk.download('stopwords')

    # Load English stopwords
    stop_words = set(stopwords.words('english'))


    filtered = set()
    for _,row in df.iterrows():

        # Tokenize and filter
        tokens = []
        if isinstance(row["description"], str):
            tokens.extend(nltk.word_tokenize(row["description"]))
        if isinstance(row["name"], str):
            tokens.extend(nltk.word_tokenize(row["name"]))
        if isinstance(row["categories"], str): 
            tokens.extend(nltk.word_tokenize(row["categories"]))
        if isinstance(row["mechanics"], str): 
            tokens.extend(nltk.word_tokenize(row["mechanics"]))
        if isinstance(row["families"], str): 
            tokens.extend(nltk.word_tokenize(row["families"]))

        filtered = filtered.union({word for word in tokens if word in stop_words and word.isalpha()})
    
    # Write to Solr-compatible stopwords file
    with open('stopwords.txt', 'w', encoding='utf-8') as f:
        for word in filtered:
            f.write(f"{word}\n")
    return

def main():
    df = pd.read_csv("cleaned_data.csv")
    get_stop_words(df)


if __name__ == "__main__":
    main()