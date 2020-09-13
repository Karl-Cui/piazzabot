import os

import pandas as pd

from preprocess import Preprocess
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
    posts = load_pickle(preproc_path)

    for post in posts:
        print(post)
