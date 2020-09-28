import spacy
import re
import pandas as pd
import numpy as np
import pickle

nlp = spacy.load("en_core_web_sm")

def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def cleaning(text):
    no_html = remove_html_tags(text)
    doc = nlp(no_html)
    filter_doc = [token.lemma_ for token in doc if not (token.is_stop or token.is_space or token.is_space or token.is_punct)]
    return ' '.join(filter_doc)



if __name__ == "__main__":
    csv_file_name = r"C:\Users\sohai\Documents\Uni 2020\csc392\CSC108&148v2\CSC108&148v2\csc108h5f_fall2019_2020-05-03\anon.contributions.csv"
    path =  r"C:\Users\sohai\Documents\Uni 2020\csc392\CSC108&148v2\CSC108&148v2\csc108h5f_fall2019_2020-05-03\data.pkl"
    df = pd.read_csv(csv_file_name)
    df.dropna(subset=["Submission HTML Removed"], inplace=True)
    posts_data = df["Submission HTML Removed"].tolist()
    #print (posts_data)
    cleaned_data = [cleaning(data) for data in posts_data]

    #np.savetxt('data.csv', np.array(cleaned_data), delimiter=',', fmt="%s")
    with open(path, 'wb') as f:
        pickle.dump(cleaned_data, f)
    print("done")
