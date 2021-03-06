from Bert.basic_semantic_search import BertSemanticSearch
from data_loader import DataLoader
from labeler import Labeler

if __name__ == "__main__":
    posts_path = r"C:\Users\karlc\Documents\uoft\CSC492\CSC108&148v2\csc148h5_spring2020_2020-05-03\anon.contributions.csv"
    path_corpus = r"C:\Users\karlc\Documents\uoft\CSC492\CSC108&148v2\csc148h5_spring2020_2020-05-03\corpus.pkl"
    path_corpus_embeddings = r"C:\Users\karlc\Documents\uoft\CSC492\CSC108&148v2\csc148h5_spring2020_2020-05-03\corpus_embeddings.pkl"
    label_path = r"C:\Users\karlc\Documents\uoft\CSC492\CSC108&148v2\csc148h5_spring2020_2020-05-03\Labeler.pkl"

    data_loader = DataLoader()
    data_loader.load(posts_path)

    qs, followup_qs = data_loader.questions_in_folder("", index=True)
    as2, followup_as2 = data_loader.questions_in_folder("assignment2", index=True)

    bert_s_s = BertSemanticSearch().from_files(path_corpus, path_corpus_embeddings)

    # label dataset
    labeler = Labeler(label_path)

    for i in range(len(as2)):
        idx, text = as2[i]
        choices_idx = bert_s_s.single_semantic_search(text, 10)

        labeler.label(
            text=text,
            text_idx=idx,
            choices=[qs[int(choice_idx)][1] for choice_idx in choices_idx],
            choices_idx=[qs[int(choice_idx)][0] for choice_idx in choices_idx]
        )
        print(labeler.labels)

    labeler.save()


