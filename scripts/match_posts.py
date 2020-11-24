"""
Script to get piazza's to csv matching
"""
import numpy as np
from utils import save_json

from bot.piazza_code import PiazzaBot
from data_loader import DataLoader

import time


# load posts
posts_path = r"C:\Users\sohai\Documents\Uni 2020\csc392\CSC108&148v2\CSC108&148v2\csc148h5_spring2020_2020-05-03\anon.contributions.csv"
data_loader = DataLoader()
data_loader.load(posts_path)

df = data_loader.get_data()
qs, _ = DataLoader.filter_latest_questions(df, subject=True)

# start piazza bot
login = np.loadtxt(r"C:\Users\sohai\Documents\Uni 2020\csc392\login.txt", dtype=str)
bot = PiazzaBot(login[0], login[1], "kg9odngyfny6s9")

# iterate through all questions
matchs_save_path = r"C:\Users\sohai\Documents\Uni 2020\csc392\CSC108&148v2\CSC108&148v2\csc148h5_spring2020_2020-05-03\matchs"
matchs = {}


posts = bot.network.iter_all_posts()
counter = 0
for post in posts:
    db_dict = bot.create_db_dict(post, None, False)
    if db_dict is None:
        continue
    try:
        subject = db_dict["subject"]
        content = db_dict["content"]
        cid = db_dict["cid"]


        for q in qs:
            if q[2] == subject:
                match = {"idx" : q[0],
                         "cid": cid,
                         "content": content,
                         "subject": subject}

                matchs[cid] = match

        if counter % 50 == 0:
            time.sleep(5)
            save_json(matchs, matchs_save_path + str(counter) + ".json")
        time.sleep(1)
        counter += 1

    except KeyError:
        continue

save_json(matchs, matchs_save_path + ".json")

"""
for i in range(len(qs)):
    content, subject = qs[i]

    # find piazza's recommendations for question from posts so far
    try:
        pred_raw = bot.get_piazza_suggestions(content)['list']
    except KeyError:
        continue

    pred = []
    for p in pred_raw:
        pred.append({key: p[key] for key in pred_keys})

    # post the post
    try:
        res = bot.create_post(
            post_folders=["general"],
            post_subject=subject,
            post_content=content
        )
        piazza_pred[res['id']] = pred

        if i % 50 == 0:
            save_json(piazza_pred, pred_save_path + str(i) + ".json")
        time.sleep(6.1)

    except:
        continue

save_json(piazza_pred, pred_save_path)
"""