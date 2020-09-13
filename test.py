import os

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from utils import *

if __name__ == "__main__":
    folder = r"C:\Users\karlc\Documents\ut\_y4\CSC492\CSC108&148v2\csc148h5_spring2020_2020-05-03"

    # # load posts data
    # data_path = os.path.join(folder, "anon.contributions.csv")
    # data = pd.read_csv(data_path)
    # data.dropna(subset=["Submission HTML Removed"], inplace=True)   # drop empty rows
    # posts = data["Submission HTML Removed"].tolist()

    # # preprocess posts data
    # pre = Preprocess()
    # posts = [pre.preprocess(post) for post in posts]

    # load / save preprocessed data
    preproc_path = os.path.join(folder, "data.pkl")

    # save_pickle(posts, preproc_path)
    data = load_pickle(preproc_path)
    data = np.array(data)

    # vectorize
    vect = TfidfVectorizer()
    vect_data = vect.fit_transform(data)

    # find cosine for a few specific posts
    cos_sim = linear_kernel(vect_data[1], vect_data).flatten()
    sim_idx = cos_sim.argsort()[:-6:-1]

    print(cos_sim[sim_idx])
    print(data[sim_idx])
