from utils import *
import os
import warnings


class Labeler:

    def __init__(self, save_path=None):
        self.save_path = save_path
        self.labels = set()

        if save_path is not None and os.path.exists(save_path):
            self.load(self.save_path)

    def label(self, text, text_idx, choices, choices_idx):
        """

        :param text:
        :param text_idx:
        :param choices:
        :param choices_idx:
        :return:
        """
        # print original post
        print("==========================================================================")
        print("Current index: " + str(text_idx))
        print("")
        print(repr(text))
        print("")
        print("==========================================================================", end="\n\n")

        # print the text of all the posts to choose from
        for i, choice in enumerate(choices):
            print(f"({str(i)}) " + repr(choice), end="\n\n")

        dupes = "s"
        while dupes == "s":

            dupes = input("Enter numbers of duplicate posts, or 's' to save:")

            if dupes == "s":
                self.save()

            else:
                for num in dupes:
                    if num.isdigit():
                        self.labels.add((text_idx, choices_idx[int(num)]))

    def save(self, path=None):
        if path is None:

            if self.save_path is None:
                warnings.warn("No path given to save labels")

            path = self.save_path

        save_pickle(list(self.labels), path=path)

    def load(self, path=None):
        if path is None:

            if self.save_path is None:
                warnings.warn("No path given to load labels from")

            path = self.save_path

        self.labels = set(load_pickle(path=path))
