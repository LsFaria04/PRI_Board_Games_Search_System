import pandas as pd
import nltk
from nltk.corpus import wordnet



def synonyms(df):
    nltk.download('wordnet')
    nltk.download('punkt_tab')
    nltk.download('stopwords')
    nltk.download('averaged_perceptron_tagger_eng')
    
    words = set()
    synonyms = dict()
    for _,row in df.iterrows():
        #get the nouns from some important text fields and normalize them

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
        
        tagged = nltk.pos_tag(tokens)
        text = [word.lower() for word, tag in tagged if tag in ('NN', 'NNS')]

        #Gets the synonyms for the nouns collected in the description
        for noun in text:
            if noun in words:
                continue
            words.add(noun)
            word_synonyms = set()
            for syn in wordnet.synsets(noun, pos=wordnet.NOUN):
                for lemma in syn.lemmas():
                    name = lemma.name().replace('_', ' ')
                    if name.lower() != noun:
                        word_synonyms.add(name)
            synonyms[noun] = word_synonyms 
    
    #Store the synonyms in a file
    with open("synonyms.txt", 'w', encoding='utf-8') as f:
        for noun, synonym in synonyms.items():
            if len(synonym) > 0:
                list_synonyms = noun + ", " + ", ".join(synonym)
                f.write(list_synonyms + "\n")
        f.close()
       
    return 

def main():
    df = pd.read_csv("cleaned_data.csv")
    synonyms(df)
    return

if __name__ == "__main__":
    main()
