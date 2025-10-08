import pandas as pd
import html


def load_data():
    '''
    Loads the data from the uncleaned datasets
    '''
    df1 = pd.read_csv("bgg_boardgames_full_sorted_part01.csv")
    df2 = pd.read_csv("bgg_boardgames_full_sorted_part02.csv")
    df3 = pd.read_csv("bgg_boardgames_full_sorted_part03.csv")

    # Concatenate the dataframes while maintaining their order
    df = pd.concat([df1, df2, df3], ignore_index=True)
    
    return df

def clean_columns(df, cols_name):
    '''
    Cleans the columns that are not relevant passed as argument
    '''
    df = df.drop(cols_name, axis = 1)
    return df

def clean_outliers(df):
    '''
    Cleans the outliers from some of the columns that can impact the performance of the search system
    '''
    # Remove max players higher than 100
    df = df[df["maxplayers"] <= 100]
    # Remove year published higher than 2025 (current year)
    df = df[df["yearpublished"] <= 2025]
    # Remove extreme playing times that have more than 500000 minutes but we may need more analisis to find the better value (including max and min)
    df = df[df["playingtime"] <= 500000]
    df = df[df["maxplaytime"] <= 500000]
    df = df[df["minplaytime"] <= 500000]
    # Remove the ones where max time < min time
    df = df[df["maxplaytime"] >= df["minplaytime"]]
    # Remove games with min age higher than 21
    df = df[df["minage"] <= 21]

    return df

def clean_null_values(df):
    '''
    Removes the null values that might cause some issues when searching 
    '''
    #Remove the rows with null descriptions
    df = df[df["description"].notna()]
    #Remove the rows with null (or 0) max and min players
    df = df[(df["maxplayers"].notna()) & (df["maxplayers"] > 0)]
    df = df[(df["minplayers"].notna()) & (df["minplayers"] > 0)]
    #Remove null yearpublish
    df = df[(df["yearpublished"].notna()) & (df["yearpublished"] != 0)]
    #Remove null publisher
    df = df[df["publishers"].notna()]
    #Remove null categories
    df = df[df["categories"].notna()]

    df = df[df["minage"].notna()]

    return df

def aggregate_columns(df):
    '''
    Aggregate columns that can be aggregated into only one
    '''
    #Aggregate min and max playing time
    df.loc[(df["playingtime"].isna()) | (df["playingtime"] == 0), "playingtime"] = (df.loc[(df["playingtime"].isna()) | (df["playingtime"] == 0), "maxplaytime"]  + df.loc[(df["playingtime"].isna()) | (df["playingtime"] == 0), "minplaytime"]) / 2
    
    #if there are still null values remove them
    df = df[(df["playingtime"].notna()) & (df["playingtime"] != 0)]

    df = df.drop(["maxplaytime", "minplaytime"], axis = 1)
    return df

def main() :
    #Load the data from the csv files
    df = load_data()

    #Clean the columns that will not be used
    df = clean_columns(df, ["type", "rank_boardgame","ranks_other", "median"])
    df = clean_outliers(df)
    df = clean_null_values(df)
    df = aggregate_columns(df)

    #Create a csv file with the resulting results for a second analisis
    df.to_csv("cleaned_data.csv", index = False)

    #Create a json file with the information of the boards after the cleaning (representation of the documents)
    df.to_json("final_data.json", orient = "records", index = False)

    return

if __name__ == "__main__":
    main()