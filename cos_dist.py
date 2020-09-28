import spacy
import re
import pandas as pd
import numpy as np
import pickle
import preproc

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

if __name__ == "__main__":
    path =  r"C:\Users\sohai\Documents\Uni 2020\csc392\CSC108&148v2\CSC108&148v2\csc108h5f_fall2019_2020-05-03\data.pkl"
    data = None
    with open(path, 'rb') as f:
        data = pickle.load(f)
    
    data = np.array(data)

    sklearn_TfidfVec = TfidfVectorizer()

    fit_data = sklearn_TfidfVec.fit_transform(data)
    text = "Can't login to Markus"

    top_n = 10

    clean_text = preproc.cleaning(text)
    fit_text = sklearn_TfidfVec.transform([clean_text])

    cos_sim = linear_kernel(fit_text, fit_data).flatten()
    sim_idx = cos_sim.argsort()[:-top_n:-1]
    print(data[sim_idx])