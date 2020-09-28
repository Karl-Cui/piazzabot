import spacy
import re
import pandas as pd
from sentence_transformers import SentenceTransformer, util
import numpy as np
import pickle


if __name__ == "__main__":
    csv_file_name = r"C:\Users\sohai\Documents\Uni 2020\csc392\CSC108&148v2\CSC108&148v2\csc108h5f_fall2019_2020-05-03\anon.contributions.csv"
    path_corpus=  r"C:\Users\sohai\Documents\Uni 2020\csc392\CSC108&148v2\CSC108&148v2\csc108h5f_fall2019_2020-05-03\corpus.pkl"
    path_corpus_embeddings=  r"C:\Users\sohai\Documents\Uni 2020\csc392\CSC108&148v2\CSC108&148v2\csc108h5f_fall2019_2020-05-03\corpus_embeddings.pkl"
    df = pd.read_csv(csv_file_name)
    df.dropna(subset=["Submission HTML Removed"], inplace=True)
    corpus = df["Submission HTML Removed"].tolist()
    embedder = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')
    corpus_embeddings = embedder.encode(corpus, convert_to_tensor=True)

    #np.savetxt('data.csv', np.array(cleaned_data), delimiter=',', fmt="%s")
    with open(path_corpus, 'wb') as f:
        pickle.dump(corpus, f)
    with open(path_corpus_embeddings, 'wb') as f:
        pickle.dump(corpus_embeddings, f)
    print("done")
