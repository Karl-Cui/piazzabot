import pickle
import json


def save_pickle(data, path):
    with open(path, 'wb') as f:
        pickle.dump(data, f)


def load_pickle(path):
    with open(path, 'rb') as f:
        return pickle.load(f)


def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f)


def load_json(path):
    with open(path) as f:
        return json.load(f)
