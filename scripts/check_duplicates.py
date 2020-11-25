import random
from data_loader import DataLoader
from labeler import Labeler

from utils import load_pickle

random.seed(202020)

if __name__ == "__main__":
    posts_path = r"C:\Users\karlc\Documents\ut\_y4\CSC492\CSC108&148v2\csc148h5_spring2020_2020-05-03\anon.contributions.csv"
    dupe_check_path = r"C:\Users\karlc\Documents\ut\_y4\CSC492\CSC108&148v2\csc148h5_spring2020_2020-05-03\dupe_check.pkl"

    data_loader = DataLoader()
    data_loader.load(posts_path)

    # map question indices to their text
    qs, followup_qs = data_loader.questions_in_folder("", index=True)
    qs = {q[0]: q[1] for q in qs}

    # load piazza's pred
    dupe_check = load_pickle(dupe_check_path)

    # label dataset
    labeler = Labeler()

    # # randomly select 100
    # indices = random.sample([i for i in range(len(dupe_check))], 100)
    # dupe_check = [dupe_check[i] for i in indices]

    for curr in dupe_check:
        idx = curr[0]
        text = qs[idx]

        labeler.label(
            text=text,
            text_idx=idx,
            choices=[qs[qidx] for qidx in curr[1:]],
            choices_idx=curr[1:]
        )
