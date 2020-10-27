from Bert.basic_semantic_search import BertSemanticSearch
from data_loader import DataLoader
from model.cosine_similarity import CosineSimilarity
from model.universal_sentence_encoder import USE
from utils import *


# paths to preprocessed data, duplicate labels, and embeddings
posts_path = r"C:\Users\karlc\Documents\ut\_y4\CSC492\CSC108&148v2\csc148h5_spring2020_2020-05-03\anon.contributions.csv"
preproc_path = r"C:\Users\karlc\Documents\ut\_y4\CSC492\CSC108&148v2\csc148h5_spring2020_2020-05-03\data.pkl"
dupe_path = r"C:\Users\karlc\Documents\ut\_y4\CSC492\CSC108&148v2\csc148h5_spring2020_2020-05-03\dupes.pkl"

# BERT
bert_corpus = r"C:\Users\karlc\Documents\ut\_y4\CSC492\CSC108&148v2\csc148h5_spring2020_2020-05-03\corpus.pkl"
bert_corpus_embeddings = r"C:\Users\karlc\Documents\ut\_y4\CSC492\CSC108&148v2\csc148h5_spring2020_2020-05-03\corpus_embeddings.pkl"


def create_duplicate_map(dupes):
    """
    Create a dictionary of {post : set(duplicate posts)} given groups of duplicate posts

    :param dupes: list of tuples, where each tuple is a set of duplicate posts
    :return: {post : set(duplicate posts)} mapping
    """
    dupes_map = {}

    for dupe in dupes:
        for i in dupe:
            dupes_map[i] = set()

            for j in dupe:
                if j != i:
                    dupes_map[i].add(j)

    return dupes_map


def benchmark_bert():
    data_loader = DataLoader()
    data_loader.load(posts_path)

    qs, followup_qs = data_loader.questions_in_folder("", include_index=True)
    as1, followup_as1 = data_loader.questions_in_folder("assignment2", include_index=True)

    # load BERT embeddings
    bert_s_s = BertSemanticSearch().from_files(bert_corpus, bert_corpus_embeddings)

    # set up dupe mapping
    dupes = load_pickle(dupe_path)
    dupes_map = create_duplicate_map(dupes)

    # evaluate
    num_correct = 0
    num_total = 0

    for i in range(len(as1)):
        idx, text = as1[i]
        pred_idx = bert_s_s.single_semantic_search(text, 4)
        pred_idx = [qs[int(pred_idx)][0] for pred_idx in pred_idx[1:]]

        # see if one of the indices in the top n is a dupe provided that the current question has a dupe
        if dupes_map.get(idx) is not None:
            num_total += 1

            for pidx in pred_idx:
                if pidx in dupes_map[idx]:
                    num_correct += 1
                    break

    return num_correct / num_total


def benchmark_cosine_sim():
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
    dupes_map = create_duplicate_map(dupes)

    # evaluate
    num_correct = 0
    num_total = 0

    for i in range(len(qs)):
        idx, _ = qs[i]
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

    return num_correct / num_total


def benchmark_use():
    data_loader = DataLoader()
    data_loader.load(posts_path)

    qs, followup_qs = data_loader.questions_in_folder("assignment2", include_index=True)
    data = [q[1] for q in qs]

    # embed using universal sentence encoder and calculate cosine similarities
    cos_sim = CosineSimilarity()
    cos_sim.set_vect(USE())

    cos_sim.fit(data)
    cos_sim.set_data(qs)

    # set up dupe mapping
    dupes = load_pickle(dupe_path)
    dupes_map = create_duplicate_map(dupes)

    # evaluate
    num_correct = 0
    num_total = 0

    for i in range(len(qs)):
        idx, _ = qs[i]
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

    return num_correct / num_total


if __name__ == "__main__":
    acc = benchmark_use()

    """
    n = 3
    ---------------------------------------
    0.5575 for cosine similarity
    0.8160 for BERT
    0.4943 for USE
    """
    print("Duplicate accuracy: " + str(acc))
