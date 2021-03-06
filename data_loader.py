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

        # convert dates into date format
        df["Created At"] = pd.to_datetime(df["Created At"])

        self.data = df

    def questions_in_folder(self, folder, index=False, timestamp=False, subject=False, qid=False, post_num=False):
        """
        Return all questions from a folder

        :param folder: name of folder to filter posts by
        :param index: if True, will return question index with question
        :param timestamp: if True will include timestamp with question
        :param subject: if True will include post title with question
        :param qid: if True will include post ID with question
        :param post_num: if True will include post number with question
        :return: list of questions, list of follow-up (probably) questions
        """
        # filter by posts from a folder
        # TODO: this isn't perfect! if we filter by "lecture" we might also get "pre-lecture_prep" for example
        mask = self.data.Folders.str.contains(folder, regex=False, na=False)    # N/A values get defaulted to False
        posts = self.data[mask.values]

        # sort by date
        posts.sort_values(by="Created At", inplace=True)

        questions, followup_questions = DataLoader.filter_latest_questions(posts,
                                                                           index=index,
                                                                           timestamp=timestamp,
                                                                           subject=subject,
                                                                           qid=qid,
                                                                           post_num=post_num)
        return questions, followup_questions

    #
    #   Filtering functions
    #

    @staticmethod
    def filter_latest_questions(posts, index=True, timestamp=False, subject=False, qid=False, post_num=False):
        """
        Find questions given a dataframe, and include information from different fields if needed. See
        questions_in_folder() method for list of fields.
        """
        questions = {}
        followup_questions = {}

        # filter by only relevant fields
        if qid:
            posts = posts[['Post Number', 'Submission HTML Removed', 'Part of Post', 'Created At', 'Subject', 'Post Number', 'id']]
        else:
            posts = posts[['Post Number', 'Submission HTML Removed', 'Part of Post', 'Created At', 'Subject', 'Post Number']]

        # drop if any field contains invalid values
        posts.dropna(subset=['Submission HTML Removed'], inplace=True)

        for row in posts.itertuples(index=True):
            # row[0] is the original index
            # row[1] is post number
            # row[2] is submission with HTML removed
            # row[3] is part of post
            # row[4] is timestamp
            # row[5] is subject
            # row[6] is post number
            # row[7] is id

            if row[3] == "started_off_question" or row[3] == "updated_question":
                questions[row[1]] = [row[2]]
                if index:
                    questions[row[1]] = [row[0]] + questions[row[1]]

                for i, include in enumerate([timestamp, subject, post_num, qid]):
                    if include:
                        questions[row[1]].append(row[i+4])

            elif row[3] == "followup" and "?" in row[2]:
                followup_questions[row[1]] = [row[2]]
                if index:
                    followup_questions[row[1]] = [row[0]] + followup_questions[row[1]]

                for i, include in enumerate([timestamp, subject, post_num, qid]):
                    if include:
                        followup_questions[row[1]].append(row[i + 4])

        questions = list(questions.values())
        followup_questions = list(followup_questions.values())

        if questions and len(questions[0]) == 1:
            questions = [q[0] for q in questions]
            followup_questions = [q[0] for q in questions]

        return questions, followup_questions

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

    qs, followup_qs = data_loader.questions_in_folder("lecture", index=True)
    print(qs)
