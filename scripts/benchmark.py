from Bert.basic_semantic_search import BertSemanticSearch
from data_loader import DataLoader
from model.cosine_similarity import CosineSimilarity
from model.universal_sentence_encoder import USE
from utils import *

from matplotlib import pyplot as plt


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


def filter_window_cos_sim(top_n=3, time_window=None):
    """
    n = 3
    ---------------------------------------
    Timestamp-agnostic:     0.5575
    Before current time:    0.4080
    3 weeks before:         0.4080
    2 weeks before:         0.3966
    1 week before:          0.3563

    :param top_n: see if correct prediction is in top n predictions
    :param time_window: number of days before post to check for duplicates
    :return: duplicate detection accuracy
    """
    data_loader = DataLoader()
    data_loader.load(posts_path)

    qs, followup_qs = data_loader.questions_in_folder("assignment2", include_index=True, include_timestamp=True)

    # # preprocess while still preserving index
    # preproc = Preprocess()
    # posts = [(idx, preproc.preprocess(text)) for (idx, text) in qs]

    # load / save preprocessed data
    # save_pickle(posts, preproc_path)
    data = load_pickle(preproc_path)
    data = [d[1] for d in data]  # d[0] is the index of the post, d[1] is the actual text, d[2] is timestamp

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
        idx, _, timestamp = qs[i]
        timestamp = timestamp.value // 10 ** 9  # convert to seconds
        pred_idx = cos_sim.find_similar(data[i])

        # no time window given: check all posts that came before
        if time_window is None:
            pred_idx = [int(sim_idx) for sim_idx, txt, ts in pred_idx if
                        ts.value // 10 ** 9 < timestamp]

        # time window given: check posts within specified number of days of asked question
        else:
            pred_idx = [int(sim_idx) for sim_idx, txt, ts in pred_idx if
                        ts.value // 10 ** 9 < timestamp <
                        ts.value // 10 ** 9 + time_window * 24 * 3600]

        pred_idx = pred_idx[:top_n]

        # see if one of the indices in the top n is a dupe provided that the current question has a dupe
        if dupes_map.get(idx) is not None:
            num_total += 1

            for pidx in pred_idx:
                if pidx in dupes_map[idx]:
                    num_correct += 1
                    break

    return num_correct / num_total


def filter_window_bert(top_n=3, time_window=None):
    """
    n = 3
    ---------------------------------------
    Timestamp-agnostic:     0.8161
    Before current time:    0.5690
    2 weeks before:         0.5000

    :param top_n: see if correct prediction is in top n predictions
    :param time_window: number of days before post to check for duplicates
    :return: duplicate detection accuracy
    """
    data_loader = DataLoader()
    data_loader.load(posts_path)

    qs, followup_qs = data_loader.questions_in_folder("", include_index=True, include_timestamp=True)
    as1, followup_as1 = data_loader.questions_in_folder("assignment2", include_index=True, include_timestamp=True)

    # load BERT embeddings
    bert_s_s = BertSemanticSearch().from_files(bert_corpus, bert_corpus_embeddings)

    # set up dupe mapping
    dupes = load_pickle(dupe_path)
    dupes_map = create_duplicate_map(dupes)

    # evaluate
    num_correct = 0
    num_total = 0

    y = []
    for top_n in range(1, 11):
        for i in range(len(as1)):
            idx, text, timestamp = as1[i]
            timestamp = timestamp.value // 10 ** 9  # convert to seconds

            pred_idx = bert_s_s.single_semantic_search(text, 100)

            # no time window given: check all posts that came before
            if time_window is None:
                pred_idx = [qs[int(pidx)][0] for pidx in pred_idx if
                            qs[int(pidx)][2].value // 10 ** 9 < timestamp]

            # time window given: check posts within specified number of days of asked question
            else:
                pred_idx = [qs[int(pidx)][0] for pidx in pred_idx if
                            qs[int(pidx)][2].value // 10 ** 9 < timestamp <
                            qs[int(pidx)][2].value // 10 ** 9 + time_window * 24 * 3600]

            pred_idx = pred_idx[:top_n]   # filter by top k entries

            # see if one of the indices in the top n is a dupe provided that the current question has a dupe
            if dupes_map.get(idx) is not None:
                num_total += 1

                for pidx in pred_idx:
                    if pidx in dupes_map[idx]:
                        num_correct += 1
                        break

        print(top_n, num_correct / num_total)
        y.append(num_correct / num_total)

    plt.scatter([i for i in range(1, 11)], y)
    plt.xlabel("Duplicate in Top n predictions")
    plt.ylabel("Accuracy")
    plt.title("Duplicate Detection Rate")
    plt.show()


if __name__ == "__main__":
    """
    n = 1
    ---------------------------------------
    0.3621 for cosine similarity
    0.6092 for BERT
    0.3276 for USE
    
    n = 3
    ---------------------------------------
    0.5575 for cosine similarity
    0.8161 for BERT
    0.8161 for Quora BERT (check that this is actually Quora BERT?)
    0.4943 for USE
    
    n = 5
    ---------------------------------------
    0.6264 for cosine similarity
    0.8735 for BERT
    0.5402 for USE
    """
    acc = filter_window_bert()
    print("Duplicate accuracy: " + str(acc))