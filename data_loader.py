import pandas as pd


class DataLoader:

    def __init__(self):
        self.data = None

    def load(self, path):
        """
        Load CSV containing all posts

        :param path: path to CSV file
        :return: None
        """
        df = pd.read_csv(path)

        # sort by date
        df["Created At"] = pd.to_datetime(df["Created At"])
        df.sort_values(by="Created At", inplace=True)

        self.data = df

    def questions_in_folder(self, folder, include_index=False):
        """
        Return all questions from a folder

        :param folder: name of folder to filter posts by
        :param include_index: if True, will return [(idx, question)] instead of [question]. Can be used to edit
                              entries in the dataframe.
        :return: list of questions, list of follow-up (probably) questions
        """
        # filter by posts from a folder
        # TODO: this isn't perfect! if we filter by "lecture" we might also get "pre-lecture_prep" for example
        mask = self.data.Folders.str.contains(folder, regex=False, na=False)    # N/A values get defaulted to False
        posts = self.data[mask.values]

        questions, followup_questions = DataLoader.filter_latest_questions(posts, include_index=include_index)
        return questions, followup_questions

    #
    #   Filtering functions
    #

    @staticmethod
    def filter_latest_questions(posts, include_index=False):
        questions = {}
        followup_questions = {}

        # filter by only relevant fields
        posts = posts[['Post Number', 'Submission HTML Removed', 'Part of Post']]

        # drop if any field contains invalid values
        posts.dropna(inplace=True)

        if include_index:
            for row in posts.itertuples(index=True):
                # index 0 is the original index
                # index 1 is post number
                # index 2 is submission with HTML removed
                # index 3 is part of post

                if row[3] == "started_off_question" or row[3] == "updated_question":
                    questions[row[1]] = (row[0], row[2])
                elif row[3] == "followup":
                    followup_questions[row[1]] = (row[0], row[2])

        else:
            for row in posts.itertuples(index=False):
                # index 0 is post number
                # index 1 is submission with HTML removed
                # index 2 is part of post

                if row[2] == "started_off_question" or row[2] == "updated_question":
                    questions[row[0]] = row[1]
                elif row[2] == "followup":
                    followup_questions[row[0]] = row[1]

        questions = list(questions.values())
        followup_questions = list(followup_questions.values())
        return questions, followup_questions

    @staticmethod
    def filter_latest_answers(posts):
        pass


if __name__ == "__main__":
    posts_path = r"C:\Users\karlc\Documents\ut\_y4\CSC492\CSC108&148v2\csc148h5_spring2020_2020-05-03\anon.contributions.csv"
    data_loader = DataLoader()
    data_loader.load(posts_path)

    qs, followup_qs = data_loader.questions_in_folder("lecture", include_index=True)
    print(qs)