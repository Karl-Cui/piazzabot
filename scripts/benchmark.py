from Bert.basic_semantic_search import BertSemanticSearch
from data_loader import DataLoader
from model.cosine_similarity import CosineSimilarity
from model.universal_sentence_encoder import USE
from utils import *

import numpy as np
from matplotlib import pyplot as plt


# paths to preprocessed data, duplicate labels, and embeddings
posts_path = r"C:\Users\karlc\Documents\ut\_y4\CSC492\CSC108&148v2\csc148h5_spring2020_2020-05-03\anon.contributions.csv"
preproc_path = r"C:\Users\karlc\Documents\ut\_y4\CSC492\CSC108&148v2\csc148h5_spring2020_2020-05-03\data.pkl"
dupe_path = r"C:\Users\karlc\Documents\ut\_y4\CSC492\CSC108&148v2\csc148h5_spring2020_2020-05-03\dupes.pkl"
piazza_match_path = r"C:\Users\karlc\Documents\ut\_y4\CSC492\CSC108&148v2\csc148h5_spring2020_2020-05-03\piazza_pred.json"

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

    qs, followup_qs = data_loader.questions_in_folder("", index=True)
    a2, followup_a2 = data_loader.questions_in_folder("assignment2", index=True)

    # load BERT embeddings
    bert_s_s = BertSemanticSearch().from_files(bert_corpus, bert_corpus_embeddings)

    # set up dupe mapping
    dupes = load_pickle(dupe_path)
    dupes_map = create_duplicate_map(dupes)

    # evaluate
    num_correct = 0
    num_total = 0

    for i in range(len(a2)):
        idx, text = a2[i]
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


def bert_sim_score(top_n=3, time_window=None):
    """
    Concerning similarity scores:

    n = 1:
        mean:  0.68802536
        median:  0.6917961
        std:  0.076929025

    n = 2:
        mean:  0.6718048
        median:  0.67678297
        std:  0.07652894

    n = 3:
        mean:  0.6718048
        median:  0.67678297
        std:  0.07652894

    n = 4:
        mean:  0.65994626
        median:  0.6663551
        std:  0.07690837

    :return:
    """
    data_loader = DataLoader()
    data_loader.load(posts_path)

    qs, followup_qs = data_loader.questions_in_folder("", index=True, timestamp=True)
    a2, followup_a2 = data_loader.questions_in_folder("assignment2", index=True, timestamp=True)

    # load BERT embeddings
    bert_s_s = BertSemanticSearch().from_files(bert_corpus, bert_corpus_embeddings)

    # set up dupe mapping
    dupes = load_pickle(dupe_path)
    dupes_map = create_duplicate_map(dupes)

    # evaluate
    num_correct = 0
    num_total = 0
    score_cutoff_no_dupe = []
    score_cutoff_dupe = []

    for i in range(len(a2)):
        idx, text, timestamp = a2[i]
        timestamp = timestamp.value // 10 ** 9  # convert to seconds

        pred_idx, cutoff = bert_s_s.single_semantic_search_with_similarity(text, 100)
        pred_idxs = []
        cutoffs = []

        # no time window given: check all posts that came before
        if time_window is None:
            for j in range(len(pred_idx)):
                pidx = pred_idx[j]

                if qs[int(pidx)][2].value // 10 ** 9 < timestamp:
                    pred_idxs.append(qs[int(pidx)][0])
                    cutoffs.append(cutoff[j])

        # time window given: check posts within specified number of days of asked question
        else:
            for j in range(len(pred_idx)):
                pidx = pred_idx[j]

                if qs[int(pidx)][2].value // 10 ** 9 < timestamp < qs[int(pidx)][2].value // 10 ** 9 + time_window * 24 * 3600:
                    pred_idxs.append(qs[int(pidx)][0])
                    cutoffs.append(cutoff[j])

        cutoff = min(cutoffs[:top_n])
        pred_idx = pred_idxs[:top_n]   # filter by top k entries

        # see if one of the indices in the top n is a dupe provided that the current question has a dupe
        found = False
        if dupes_map.get(idx) is not None:
            num_total += 1

            for pidx in pred_idx:
                if pidx in dupes_map[idx]:
                    num_correct += 1
                    found = True
                    score_cutoff_dupe.append(cutoff)
                    break

        if not found:
            score_cutoff_no_dupe.append(cutoff)

    """Score cutoff analysis"""
    score_cutoff_no_dupe = np.array(score_cutoff_no_dupe)
    score_cutoff_dupe = np.array(score_cutoff_dupe)

    # print("mean: ", np.mean(score_cutoff))
    # print("median: ", np.median(score_cutoff))
    # print("std: ", np.std(score_cutoff))

    # plot score cutoff
    plt.hist([score_cutoff_dupe, score_cutoff_no_dupe], bins=30, stacked=True)
    plt.legend(["Posts with duplicates", "Posts with no duplicates"])
    plt.xlabel("Similarity score")
    plt.ylabel("Number of samples")
    plt.title("Distribution of similarity score cutoff for n={0}".format(top_n))
    plt.show()

    return num_correct / num_total


def bert_sim_score_threshold(time_window=None, threshold=0.):
    """
    Use threshold for cosine similarity
    """
    data_loader = DataLoader()
    data_loader.load(posts_path)

    qs, followup_qs = data_loader.questions_in_folder("", index=True, timestamp=True)
    a2, followup_a2 = data_loader.questions_in_folder("assignment2", index=True, timestamp=True)

    # load BERT embeddings
    bert_s_s = BertSemanticSearch().from_files(bert_corpus, bert_corpus_embeddings)

    # set up dupe mapping
    dupes = load_pickle(dupe_path)
    dupes_map = create_duplicate_map(dupes)

    # evaluate
    num_correct = 0
    num_total = 0
    pred_entry_len_dupe = {}
    pred_entry_len_no_dupe = {}

    for i in range(len(a2)):
        idx, text, timestamp = a2[i]
        timestamp = timestamp.value // 10 ** 9  # convert to seconds

        pred_idx = bert_s_s.single_semantic_search_using_threshold(text, 100, threshold=threshold)

        # no time window given: check all posts that came before
        if time_window is None:
            pred_idx = [qs[int(pidx)][0] for pidx in pred_idx if
                        qs[int(pidx)][2].value // 10 ** 9 < timestamp]

        # time window given: check posts within specified number of days of asked question
        else:
            pred_idx = [qs[int(pidx)][0] for pidx in pred_idx if
                        qs[int(pidx)][2].value // 10 ** 9 < timestamp <
                        qs[int(pidx)][2].value // 10 ** 9 + time_window * 24 * 3600]

        # count number of entries
        num_entries = len(pred_idx)

        # see if one of the indices in the top n is a dupe provided that the current question has a dupe
        found = False
        if dupes_map.get(idx) is not None:
            num_total += 1

            for pidx in pred_idx:
                if pidx in dupes_map[idx]:
                    num_correct += 1
                    found = True
                    pred_entry_len_dupe[num_entries] = pred_entry_len_dupe.get(num_entries, 0) + 1
                    break

        if not found:
            pred_entry_len_no_dupe[num_entries] = pred_entry_len_no_dupe.get(num_entries, 0) + 1

    x = [i for i in range(100)]
    y_dupe = [pred_entry_len_dupe[i] if i in pred_entry_len_dupe else 0 for i in range(100)]
    plt.bar(x=x, height=y_dupe)

    y_no_dupe = [pred_entry_len_no_dupe[i] if i in pred_entry_len_no_dupe else 0 for i in range(100)]
    plt.bar(x=x, height=y_no_dupe, bottom=y_dupe)

    plt.title("Distribution of number of predictions for similarity threshold {0}".format(threshold))
    plt.xlabel("Number of predictions")
    plt.ylabel("Number of posts")
    plt.show()

    return num_correct / num_total


def benchmark_cosine_sim():
    data_loader = DataLoader()
    data_loader.load(posts_path)

    qs, followup_qs = data_loader.questions_in_folder("assignment2", index=True)

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

    qs, followup_qs = data_loader.questions_in_folder("assignment2", index=True)
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

    qs, followup_qs = data_loader.questions_in_folder("assignment2", index=True, timestamp=True)

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

    qs, followup_qs = data_loader.questions_in_folder("", index=True, timestamp=True)
    a2, followup_a2 = data_loader.questions_in_folder("assignment2", index=True, timestamp=True)

    # load BERT embeddings
    bert_s_s = BertSemanticSearch().from_files(bert_corpus, bert_corpus_embeddings)

    # set up dupe mapping
    dupes = load_pickle(dupe_path)
    dupes_map = create_duplicate_map(dupes)

    # evaluate
    num_correct = 0
    num_total = 0

    for i in range(len(a2)):
        idx, text, timestamp = a2[i]
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

    return num_correct / num_total


def piazza_pred(top_n=3):
    """
    Evaluate accuracy of piazza's duplicate predictions

    :param top_n: see if correct prediction is in top n predictions
    :return: duplicate detection accuracy
    """
    data_loader = DataLoader()
    data_loader.load(posts_path)

    qs, followup_qs = data_loader.questions_in_folder("", index=True, timestamp=False, qid=True)
    a2, followup_a2 = data_loader.questions_in_folder("assignment2", index=True, timestamp=False, qid=True)

    # load matches by Piazza (note that these are already sorted by some sort of confidence score)
    matches = load_json(piazza_match_path)
    id_to_idx = {q[-1]: q[0] for q in qs}   # mapping from a question's ID to its index

    # set up dupe mapping
    dupes = load_pickle(dupe_path)
    dupes_map = create_duplicate_map(dupes)

    # evaluate
    num_correct = 0
    num_total = 0
    num_keyerror = 0

    for i in range(len(a2)):
        idx, _, qid = a2[i]

        if dupes_map.get(idx) is not None:

            pred_id = matches[qid]
            pred_id = [p['id'] for p in pred_id]   # only take ids
            pred_id = pred_id[:top_n]              # filter by top k entries

            try:
                pred_idx = [id_to_idx[p] for p in pred_id]   # convert from ID to index
            except KeyError:
                num_keyerror += 1

            # see if one of the indices in the top n is a dupe provided that the current question has a dupe
            num_total += 1

            for pidx in pred_idx:
                if pidx in dupes_map[idx]:
                    num_correct += 1
                    break

    print(num_total, num_keyerror)
    return num_correct / num_total


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
    acc = filter_window_bert(top_n=3)
    print("BERT duplicate accuracy: " + str(acc))

    acc = piazza_pred(top_n=3)
    print("Piazza duplicate accuracy: " + str(acc))
