import numpy as np
import tensorflow_hub as hub


class USE:

    def __init__(self):
        model_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
        self.model = hub.load(model_url)

    def transform(self, data):
        """
        Given text data, embed with universal sentence encoder, and convert from tensor to numpy array

        :param data: list of string of length n
        :return: (n, 512) ndarray of embedded data
        """
        data = self.model(data)
        data = np.array(data)

        return data

    def fit_transform(self, *args, **kwargs):
        """Same as self.transform()"""
        return self.transform(*args, **kwargs)
