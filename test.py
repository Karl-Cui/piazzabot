from data_loader import DataLoader
from model.cosine_similarity import CosineSimilarity
from utils import *

from labeler import Labeler

if __name__ == "__main__":
    posts_path = r"C:\Users\karlc\Documents\ut\_y4\CSC492\CSC108&148v2\csc148h5_spring2020_2020-05-03\anon.contributions.csv"
    preproc_path = r"C:\Users\karlc\Documents\ut\_y4\CSC492\CSC108&148v2\csc148h5_spring2020_2020-05-03\data.pkl"
    label_path = r"C:\Users\karlc\Documents\ut\_y4\CSC492\CSC108&148v2\csc148h5_spring2020_2020-05-03\labeled.pkl"

    data_loader = DataLoader()
    data_loader.load(posts_path)

    qs, followup_qs = data_loader.questions_in_folder("lecture", include_index=True)

    # # preprocess while still preserving index
    # preproc = Preprocess()
    # posts = [(idx, preproc.preprocess(text)) for (idx, text) in qs]

    # load / save preprocessed data
    # save_pickle(posts, preproc_path)
    data = load_pickle(preproc_path)
    data = [d[1] for d in data]  # d[0] is the index of the post, d[1] is the actual text

    # train basic similarity model
    cos_sim = CosineSimilarity()
    cos_sim.fit(data)
    cos_sim.set_data(qs)

    # label dataset
    labeler = Labeler(label_path)

    for i in range(len(qs)):
        idx, text = qs[i]
        idx_and_sim = cos_sim.find_similar(data[i], top_n=11)

        # remove duplicate entry
        idx_and_sim = [(int(sim_idx), sim) for (sim_idx, sim) in idx_and_sim if int(sim_idx) != idx]

        labeler.label(
            text=text,
            text_idx=idx,
            choices=[x[1] for x in idx_and_sim],
            choices_idx=[x[0] for x in idx_and_sim]
        )

    labeler.save()

