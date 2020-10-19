import pandas as pd
from sentence_transformers import SentenceTransformer, util
import numpy as np
import utils
from data_loader import DataLoader

class BertSemanticSearch:

    def __init__(self, corpus=None, corpus_embeddings=None):
        self.embedder = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')
        self.corpus = corpus
        self.corpus_embeddings = corpus_embeddings

    @classmethod
    def from_files(cls, path_corpus: str, path_corpus_embeddings: str) -> 'BertSemanticSearch':
    	return cls(corpus=utils.load_pickle(path_corpus), corpus_embeddings=utils.load_pickle(path_corpus_embeddings))

    def save_data(self, path_corpus, path_corpus_embeddings):
        utils.save_pickle(self.corpus, path_corpus)
        utils.save_pickle(self.corpus_embeddings, path_corpus_embeddings)

    def set_corpus(self, corpus):
        self.corpus = corpus

    def preprocess_corpus(self):
        self.corpus_embeddings = self.embedder.encode(self.corpus, convert_to_tensor=True)

    def semantic_search(self, queries, top_k=5):
        
        for query in queries:
            query_embedding = self.embedder.encode(query, convert_to_tensor=True)
            cos_scores = util.pytorch_cos_sim(query_embedding, self.corpus_embeddings)[0]
            cos_scores = cos_scores.cpu()

            #We use np.argpartition, to only partially sort the top_k results
            top_results = np.argpartition(-cos_scores, range(top_k))[0:top_k]

            print("\n\n======================\n\n")
            print("Query:", query)
            print("\nTop {} most similar sentences in corpus:".format(top_k))

            for idx in top_results[0:top_k]:
                print("\n\n (index={})======================\n\n".format(idx))
                print(self.corpus[idx].strip(), "(Score: %.4f)" % (cos_scores[idx]))

    def single_semantic_search(self, query, top_k=5, log=False):

        query_embedding = self.embedder.encode(query, convert_to_tensor=True)
        cos_scores = util.pytorch_cos_sim(query_embedding, self.corpus_embeddings)[0]
        cos_scores = cos_scores.cpu()

        # We use np.argpartition, to only partially sort the top_k results
        top_results = np.argpartition(-cos_scores, range(top_k))[0:top_k]

        if log:
            print("\n\n======================\n\n")
            print("Query:", query)
            print("\nTop {} most similar sentences in corpus:".format(top_k))

            for idx in top_results[0:top_k]:
                print("\n\n (index={})======================\n\n".format(idx))
                print(self.corpus[idx].strip(), "(Score: %.4f)" % (cos_scores[idx]))

        return top_results[0:top_k]

if __name__ == "__main__":
    csv_file_name = r"C:\Users\sohai\Documents\Uni 2020\csc392\CSC108&148v2\CSC108&148v2\csc148h5_spring2020_2020-05-03\anon.contributions.csv"
    path_corpus=  r"C:\Users\sohai\Documents\Uni 2020\csc392\CSC108&148v2\CSC108&148v2\csc148h5_spring2020_2020-05-03\corpus.pkl"
    path_corpus_embeddings=  r"C:\Users\sohai\Documents\Uni 2020\csc392\CSC108&148v2\CSC108&148v2\csc148h5_spring2020_2020-05-03\corpus_embeddings.pkl"
    #df = pd.read_csv(csv_file_name)
    #df.dropna(subset=["Submission HTML Removed"], inplace=True)
    #corpus = df["Submission HTML Removed"].tolist()

    data_loader = DataLoader()
    data_loader.load(csv_file_name)

    qs, followup_qs = data_loader.questions_in_folder("", include_index=False)

    bert_s_s = BertSemanticSearch()
    bert_s_s.set_corpus(qs)
    bert_s_s.preprocess_corpus()
    bert_s_s.save_data(path_corpus, path_corpus_embeddings)
    print("done")