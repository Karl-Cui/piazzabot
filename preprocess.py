import re
import html

import spacy


class Preprocess:

    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def preprocess(self, doc):
        """
        Preprocess string of text.

        TODO: should we remove URLs? They may lead to piazza posts

        Notes:
        - we use regex to remove the URLs because spacy often interprets python file names as URLs
        """
        doc = html.unescape(doc)    # substitute out HTML entities
        doc = re.sub(r"https?://\S+", " ", doc)  # remove URLs

        doc = self.nlp(doc)         # spacy magic

        doc = [token.lemma_ for token in doc if not (   # lemmatize
            token.is_punct or       # remove punctuation
            token.is_space or       # remove spaces and newlines
            token.is_stop           # remove stop words
        )]

        doc = " ".join(doc)
        doc = doc.lower()           # take lowercase

        return doc
