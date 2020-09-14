import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from preprocess import Preprocess


class CosineSimilarity:

    def __init__(self):
        self.vect = TfidfVectorizer()

        self.data = None
        self.vect_data = None

        self.pre = Preprocess()

    def fit(self, data):
        """
        Fit to (preprocessed) data given

        :param data: list of str
        :return: None
        """
        if not isinstance(data, np.ndarray):
            data = np.array(data)

        self.data = data
        self.vect_data = self.vect.fit_transform(data)

    def find_similar(self, text, top_n):
        """
        Find top n texts (from set of fitted texts) that are most similar to the one given

        :param text: str that we want to find most similar to
        :param top_n: number of most similar matches to find
        :return: list of similar texts
        """
        top_n = min(top_n + 1, self.data.size)  # make sure smaller than dataset size

        text = self.pre.preprocess(text)
        text = self.vect.transform([text])

        cos_sim = linear_kernel(text, self.vect_data).flatten()
        sim_idx = cos_sim.argsort()[:-top_n:-1]

        return self.data[sim_idx]
