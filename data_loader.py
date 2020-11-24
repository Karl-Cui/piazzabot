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

    def questions_in_folder(self, folder, index=False, timestamp=False, subject=False, qid=False):
        """
        Return all questions from a folder

        :param folder: name of folder to filter posts by
        :param index: if True, will return question index with question
        :param timestamp: if True will include timestamp with question
        :param subject: if True will include post title with question
        :param qid: if True will include post ID with question
        :return: list of questions, list of follow-up (probably) questions
        """
        # filter by posts from a folder
        # TODO: this isn't perfect! if we filter by "lecture" we might also get "pre-lecture_prep" for example
        mask = self.data.Folders.str.contains(folder, regex=False, na=False)    # N/A values get defaulted to False
        posts = self.data[mask.values]

        questions, followup_questions = DataLoader.filter_latest_questions(posts,
                                                                           index=index,
                                                                           timestamp=timestamp,
                                                                           subject=subject,
                                                                           qid=qid)
        return questions, followup_questions

    #
    #   Filtering functions
    #

    @staticmethod
    def filter_latest_questions(posts, index=True, timestamp=False, subject=False, qid=False):
        """
        Find questions given a dataframe, and include information from different fields if needed. See
        questions_in_folder() method for list of fields.
        """
        questions = {}
        followup_questions = {}

        # filter by only relevant fields
        posts = posts[['Post Number', 'Submission HTML Removed', 'Part of Post', 'Created At', "Subject", "id"]]

        # drop if any field contains invalid values
        posts.dropna(subset=['Submission HTML Removed'], inplace=True)

        for row in posts.itertuples(index=True):
            # row[0] is the original index
            # row[1] is post number
            # row[2] is submission with HTML removed
            # row[3] is part of post
            # row[4] is timestamp
            # row[5] is subject
            # row[6] is id

            if row[3] == "started_off_question" or row[3] == "updated_question":
                questions[row[1]] = [row[2]]
                if index:
                    questions[row[1]] = [row[0]] + questions[row[1]]
                if timestamp:
                    questions[row[1]].append(row[4])
                if subject:
                    questions[row[1]].append(row[5])
                if qid:
                    questions[row[1]].append(row[6])

            elif row[3] == "followup":
                followup_questions[row[1]] = [row[2]]
                if index:
                    followup_questions[row[1]] = [row[0]] + followup_questions[row[1]]
                if timestamp:
                    followup_questions[row[1]].append(row[4])
                if subject:
                    followup_questions[row[1]].append(row[5])
                if qid:
                    questions[row[1]].append(row[6])

        questions = list(questions.values())
        followup_questions = list(followup_questions.values())

        if questions and len(questions[0]) == 1:
            questions = [q[0] for q in questions]
            followup_questions = [q[0] for q in questions]

        return questions, followup_questions

    @staticmethod
    def filter_latest_answers(posts):
        pass

    #
    #   Getters and setters
    #

    def get_data(self):
        return self.data

    def get_all_questions(self):
        """
        Return dataframe only containing questions

        :return: pandas dataframe
        """
        return self.data[
            (self.data["Part of Post"] == "started_off_question") |
            (self.data["Part of Post"] == "updated_question")
        ]


if __name__ == "__main__":
    posts_path = r"C:\Users\karlc\Documents\ut\_y4\CSC492\CSC108&148v2\csc148h5_spring2020_2020-05-03\anon.contributions.csv"
    data_loader = DataLoader()
    data_loader.load(posts_path)

    qs, followup_qs = data_loader.questions_in_folder("lecture", include_index=True)
    print(qs)
