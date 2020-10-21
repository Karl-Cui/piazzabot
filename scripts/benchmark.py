from data_loader import DataLoader
from model.cosine_similarity import CosineSimilarity
from utils import *


if __name__ == "__main__":
    posts_path = r"C:\Users\karlc\Documents\ut\_y4\CSC492\CSC108&148v2\csc148h5_spring2020_2020-05-03\anon.contributions.csv"
    preproc_path = r"C:\Users\karlc\Documents\ut\_y4\CSC492\CSC108&148v2\csc148h5_spring2020_2020-05-03\data.pkl"
    label_path = r"C:\Users\karlc\Documents\ut\_y4\CSC492\CSC108&148v2\csc148h5_spring2020_2020-05-03\labeled.pkl"
    dupe_path = r"C:\Users\karlc\Documents\ut\_y4\CSC492\CSC108&148v2\csc148h5_spring2020_2020-05-03\dupes.pkl"

    data_loader = DataLoader()
    data_loader.load(posts_path)

    qs, followup_qs = data_loader.questions_in_folder("assignment2", include_index=True)

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

    # set up dupe mapping
    dupes = load_pickle(dupe_path)
    dupes_map = {}

    for dupe in dupes:
        for i in dupe:
            dupes_map[i] = set()

            for j in dupe:
                if j != i:
                    dupes_map[i].add(j)

    # evaluate
    num_correct = 0
    num_total = 0

    for i in range(len(qs)):
        idx, text = qs[i]
        pred_idx = cos_sim.find_similar(data[i], top_n=4)

        # remove duplicate entry
        pred_idx = [int(sim_idx) for (sim_idx, sim) in pred_idx]
        pred_idx = [sim_idx for sim_idx in pred_idx if sim_idx != idx]

        # see if one of the indices in the top n is a dupe provided that the current question has a dupe
        if dupes_map.get(idx) is not None:
            num_total += 1

            for pidx in pred_idx:
                if pidx in dupes_map[idx]:
                    num_correct += 1
                    break

    """
    0.5575 for cosine similarity, n = 3
    0.8160 for BERT, n=3
    """
    print("Duplicate accuracy: " + str(num_correct / num_total))
