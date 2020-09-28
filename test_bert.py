from Bert.basic_semantic_search import BertSemanticSearch
from data_loader import DataLoader


if __name__ == "__main__":
    posts_path = r"C:\Users\sohai\Documents\Uni 2020\csc392\CSC108&148v2\CSC108&148v2\csc148h5_spring2020_2020-05-03\anon.contributions.csv"
    path_corpus=  r"C:\Users\sohai\Documents\Uni 2020\csc392\CSC108&148v2\CSC108&148v2\csc148h5_spring2020_2020-05-03\corpus.pkl"
    path_corpus_embeddings=  r"C:\Users\sohai\Documents\Uni 2020\csc392\CSC108&148v2\CSC108&148v2\csc148h5_spring2020_2020-05-03\corpus_embeddings.pkl"

    data_loader = DataLoader()
    data_loader.load(posts_path)

    qs, followup_qs = data_loader.questions_in_folder("lecture", include_index=False)
    print(qs[1])

    bert_s_s = BertSemanticSearch().from_files(path_corpus, path_corpus_embeddings)

    bert_s_s.semantic_search(qs[-5:])

