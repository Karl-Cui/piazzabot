# PiazzaBot

PiazzaBot aims to reduce the workload of TAs and professors on Piazza by asking students whether their questions are duplicates or not before letting them post.

The basic workflow is a follows:
- A student posts a question
- PiazzaBot sets the visibility of that question to private
- PiazzaBot presents the student with several possible duplicate posts, and several options. The student has to decide if:
    * The question is a duplicate of one of the posts PiazzaBot recommended. Nothing is done in this case.
    * The question is similar to one of the posts PiazzaBot recommended. The question is instead posted as follow-up to whichever post PiazzaBot recommended.
    * the question is not similar to any of the posts PiazzaBot recommended. The question's visibility gets set to public and will be answered by students, professors, or TAs like usual.

## Installation

PiazzaBot runs on Python 3.7. Use [pip](https://pip.pypa.io/en/stable/) to install all the requirements. We recommend doing so in a virtual environment.

```bash
pip install -r requirements.txt
```

In addition to these dependencies, PiazzaBot also requires MongoDB.

## Usage

There are several different tools in this repository.

### PiazzaBot

Files for the actual bot can be found under the `bot/` folder. There are two main components:
- `db.py` is code for the database. This is used to check whether there are any new posts on Piazza.
- `piazza_code.py` is the code for the actual bot, which contains methods for interfacing with Piazza's API, our database, and our model. The `heart_beat()` function is used to check Piazza for new posts, respond accordingly, and update our database's entries.

### Benchmarking different models 

We benchmarked feature generation using:
- [TF-IDF](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
- [BERT](https://ai.googleblog.com/2018/11/open-sourcing-bert-state-of-art-pre.html)
- [USE](https://www.tensorflow.org/hub/tutorials/semantic_similarity_with_tf_hub_universal_encoder)

Afterwards, we apply cosine similarity to get scores indicating how similar pairs of questions are. We compare the pairs of questions that the models predict are most similar with the duplicates that we manually labeled to score the model.

Some of these benchmarks take optional arguments for:
- `top_n`: the number of highest score ("confidence") predictions to look at
- `time_window`: the number of days before a specific post to search for duplicate posts

### Labeling

To label duplicates, we used `labeler.py`. The `label()` takes in the text of a question (to display to whoever's labeling), the index of that question in the CSV, the texts of questions that are possible duplicates (also for displaying), and their respective indices. Then, we called `label()` for every question.

It would be infeasible to check whether a question is a duplicate with every other question. Instead, we opted to use BERT to find the top 10 most similar questions with BERT first, then manually check for duplicates.

