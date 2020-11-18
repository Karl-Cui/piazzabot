"""
Script to get piazza's predictions for all the posts in a corpus
"""
import numpy as np
from utils import save_json

from bot.piazza_code import PiazzaBot
from data_loader import DataLoader


# load posts
posts_path = r"C:\Users\karlc\Documents\ut\_y4\CSC492\CSC108&148v2\csc148h5_spring2020_2020-05-03\anon.contributions.csv"
data_loader = DataLoader()
data_loader.load(posts_path)

df = data_loader.get_data()
qs, _ = DataLoader.filter_latest_questions(df, subject=True)

# start piazza bot
login = np.loadtxt(r"C:\Users\karlc\Documents\ut\_y4\CSC492\login.txt", dtype=str)
bot = PiazzaBot(login[0], login[1], "kg9odngyfny6s9")

# iterate through all questions
piazza_pred = []
for q in qs[:10]:

    content, subject = q

    # find piazza's recommendations for question from posts so far
    pred = bot.get_piazza_suggestions(content)
    piazza_pred.append(pred)

    # post the post
    bot.create_post(
        post_folders=["general"],
        post_subject=subject,
        post_content=content
    )

pred_save_path = r"C:\Users\karlc\Documents\ut\_y4\CSC492\CSC108&148v2\csc148h5_spring2020_2020-05-03\piazza_pred.json"
save_json(piazza_pred, pred_save_path)
