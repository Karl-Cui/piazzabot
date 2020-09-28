import spacy
import re
import pandas as pd
from sentence_transformers import SentenceTransformer, util
import numpy as np
import pickle
import preproc

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

if __name__ == "__main__":
    path_corpus=  r"C:\Users\sohai\Documents\Uni 2020\csc392\CSC108&148v2\CSC108&148v2\csc108h5f_fall2019_2020-05-03\corpus.pkl"
    path_corpus_embeddings=  r"C:\Users\sohai\Documents\Uni 2020\csc392\CSC108&148v2\CSC108&148v2\csc108h5f_fall2019_2020-05-03\corpus_embeddings.pkl"

    embedder = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')

    corpus = None
    with open(path_corpus, 'rb') as f:
        corpus = pickle.load(f)

    corpus_embeddings = None
    with open(path_corpus_embeddings, 'rb') as f:
        corpus_embeddings = pickle.load(f)

    # Query sentences:
    queries = ['A man is eating pasta.']


    # Find the closest 5 sentences of the corpus for each query sentence based on cosine similarity
    top_k = 5
    for query in queries:
        query_embedding = embedder.encode(query, convert_to_tensor=True)
        cos_scores = util.pytorch_cos_sim(query_embedding, corpus_embeddings)[0]
        cos_scores = cos_scores.cpu()

        #We use np.argpartition, to only partially sort the top_k results
        top_results = np.argpartition(-cos_scores, range(top_k))[0:top_k]

        print("\n\n======================\n\n")
        print("Query:", query)
        print("\nTop 5 most similar sentences in corpus:")

        for idx in top_results[0:top_k]:
            print(corpus[idx].strip(), "(Score: %.4f)" % (cos_scores[idx]))