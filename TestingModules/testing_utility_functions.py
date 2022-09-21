import pickle as pkl


def load_pickle_from_file(file):
    with open(file, "rb") as f:
        return pkl.load(f)
