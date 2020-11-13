import pickle
import sched
import time
import torch

import numpy as np
from piazza_api import Piazza

from Bert.basic_semantic_search import BertSemanticSearch
from bot.db import MongoDBManger


class PiazzaBot(object):

    def __init__(self, user, password, class_id, corpus=None, corpus_embeddings=None, default_bert=True):
        self.p = Piazza()
        self.p.user_login(user, password)
        self.class_id = class_id
        self.user_profile = self.p.get_user_profile()
        self.network = self.p.network(class_id)
        self.DB_manger = MongoDBManger()
        self.bert = BertSemanticSearch(corpus, corpus_embeddings, default_bert)
        self.parallel_cid_list = []

    def heart_beat(self):
        """
        triggers the heart beat code which process all new posts and puts the data for them into the db and also
        make new postings and suggestions for posts in our

        :return: NA
        """
        posts = self.network.iter_all_posts()
        for post in posts:
            try:
                cid = post["id"]
                query = {"cid": cid}
                result = self.DB_manger.find(query)
                db_dict = self.create_db_dict(post, result)

                # TODO: remove HTML tags

                if result is None and db_dict is not None:
                    self.DB_manger.insert(db_dict)
                    if not db_dict["is_marked"]:
                        self.create_piazza_bot_follow_up(cid, "Piazza Bot is trying to process this post")
                        self.make_private(db_dict)

                elif db_dict is not None:
                    if not db_dict["is_processed"] and db_dict["is_marked"] and len(self.parallel_cid_list) != 0:
                        self.make_piazza_suggestions(db_dict, cid)
                    elif not db_dict["is_marked"]:
                        print("here")
                        self.create_piazza_bot_follow_up(cid, "Piazza Bot is trying to process this post")
                        self.make_private(db_dict)

                    self.DB_manger.insert_update(query, db_dict)
                    # update the value in the db if the change_log or history has changed
                    if db_dict["change_log_len"] > result["change_log_len"] or db_dict["revision"] > result["revision"]:
                        self.DB_manger.insert_update(query, db_dict)

            except KeyError:
                print("no cid")

    def generate_embeddings(self):
        """
        generate the embeddings for all the current posts in the data base

        :return: NA
        """
        docs = self.DB_manger.get_all()
        if docs is None:
            return 1

        corpus = []
        corpus_embeddings = []
        parallel_cid_list_local = []
        for doc in docs:
            corpus.append(doc["content"])
            corpus_embeddings.append(pickle.loads(doc["encoding"]))
            parallel_cid_list_local.append(doc["cid"])

        # turn list of loaded tensors to a single tensor
        corpus_embeddings = [torch.unsqueeze(t, dim=0) for t in corpus_embeddings]
        corpus_embeddings = torch.cat(corpus_embeddings, dim=0)

        self.bert.set_corpus(corpus)
        self.bert.set_corpus_embeddings(corpus_embeddings)
        self.parallel_cid_list = parallel_cid_list_local

    def create_db_dict(self, post, old_post):
        """
        generate the embeddings for all the current posts in the data base

        :param post: the new post json data we want to process into a dict we can put into the db
        :param old_post: old db value for the current post
        :return: post dict formatted for the DB
        """
        try:
            cid = post["id"]
            history = post["history"]
            change_log_len = len(post["change_log"])
            revision = len(history)
            cur_post_content = history[-1]
            uid = self.find_uid(cur_post_content)
            if "gd6v7134AUa" == uid:
                return None

            post_type = post["type"]
            post_folders = post['folders']
            post_subject = cur_post_content['subject']
            post_content = cur_post_content['content']
            is_marked_by_pb, is_processed, mark_id = self.is_marked_by_piazza_bot(post["children"], old_post)

            new_value = {"cid": cid,
                         "revision": revision,
                         "change_log_len": change_log_len,
                         "uid": uid,
                         "type": post_type,
                         "folders": post_folders,
                         "subject": post_subject,
                         "content": post_content,
                         "is_marked": is_marked_by_pb,
                         "mark_id": mark_id,
                         "is_processed": is_processed}
            # generate a new embedding if this is first time this post is being added to the db or if there was a content update
            if old_post is None or revision > old_post["revision"]:
                encoding = pickle.dumps(self.bert.encode_content(post_content))
                print(encoding)
                new_value["encoding"] = encoding
            return new_value

        except KeyError as e:
            print(e)
            return None

    def is_marked_by_piazza_bot(self, children, old_post):
        """
        figure out of the current post has been marked by the bot and processed. if the current post has been marked
        then get the cid for the marking follow up
        :param children: current children posts(follow ups) for the current post
        :param old_post: old db value for the current post
        :return: boolean, boolean, cid
        """
        len_children = len(children)
        if len_children == 0:
            print("getting childern len 0")
            return False, False, "None"

        for follow_up in children:
            if follow_up['type'] == "i_answer":
                return True, True, "None"

            subject = follow_up['subject']
            if subject == "Piazza Bot is trying to process this post":
                return True, False, follow_up['id']
            elif subject == "Piazza Bot Has Processed this post":
                return True, True, follow_up['id']
            elif len(subject) > 24 and subject[:24] == '<p><b>Piazza Bot</b></p>':
                return True, False, follow_up['id']

        if old_post is not None and old_post["is_marked"]:
            return True, True, old_post["mark_id"]

        return False, False, "None"

    def make_private(self, db_dict):
        """
        make the post associate with the current db dict object private
        :param db_dict: db dict object of the post we want to make private
        :return: 1 if successful else 0
        """
        try:
            if "gd6v7134AUa" != db_dict["uid"]:
                self.update_post(db_dict["cid"], db_dict["type"], db_dict["revision"], db_dict["folders"], db_dict["subject"], db_dict["content"], False)

            return 1
        except KeyError:
            return 0

    def make_suggestion_string(self, cur_cid, post_cid):
        link = '<p><a href="https://piazza.com/class/kg9odngyfny6s9?cid={}" target="_blank" rel="noopener">Potential Duplicate of @{}</a></p>'.format(cur_cid, cur_cid)
        mark_dup = '<p><a href="http://127.0.0.1:5000/api/dup/{}/{}" target="_blank" rel="noopener">Mark Current Post as Duplicate of @{}</a>'.format(post_cid, cur_cid, cur_cid)
        mark_followup = 'or <a href="http://127.0.0.1:5000/api/followup/{}/{}" target="_blank" rel="noopener">Mark Current Post as Follow up of @{}</a></p>'.format(post_cid, cur_cid, cur_cid)
        return link + mark_dup + mark_followup

    def make_piazza_suggestions(self, db_dict, cid):
        #TODO add getting suggestions code
        msg = '<p><b>Piazza Bot</b></p><p><a href="http://127.0.0.1:5000/api/post/{}" target="_blank" rel="noopener">Make Post Public</a></p>'.format(cid)

        try:
            if "gd6v7134AUa" != db_dict["uid"]:
                topk_idxs = self.bert.single_semantic_search(db_dict["content"], top_k=3)
                topk_cids = [self.parallel_cid_list[idx] for idx in topk_idxs]

                for dup_cid in topk_cids:
                    if dup_cid != cid:
                        msg += self.make_suggestion_string(dup_cid, cid)

                self.update_follow_up(db_dict["mark_id"], msg)

            return 1
        except KeyError:
            return 0

    def find_uid(self, cur_post_content):
        """
        find the uid from the most latest post history(content)

        :param cur_post_content: the content params fot he post we are working on
        :return: the uid for the user who made the last edit on this post
        """
        try:
            uid = cur_post_content["uid"]
        except KeyError:
            uid = ""
        return uid

    def update_post(self, cid, post_type, revision, post_folders, post_subject, post_content, visibility_all=True):
        """Update a post

        :param cid: cid of the post we want to update
        :param post_type: the type we want to change the post to "note", "question" or "poll"
        :param revision:
        :param post_folders:
        :param post_subject:
        :param post_content:
        :param visibility_all: change post visibility from all to just the instructors and original poster
        :return: if the post update was successful
        """

        params = {
            "cid": cid,
            "subject": post_subject,
            "content": post_content,
            "folders": post_folders,
            "type": post_type,
            "revision": revision,
            "visibility": "all" if visibility_all else "private"
        }
        print(params)
        return self.network._rpc.content_update(params)

    def create_piazza_bot_follow_up(self, cid, content, ionly=False):
        """Create a follow-up on a post.

        :param cid: cid of the post we want to add this follow up too
        :param content: content of the follow up post
        :param ionly: make the visibility of the follow only instructors
        :return: follow up was created
        """

        params = {
            "cid": cid,
            "type": "followup",
            "subject": content,
            "content": "",
        }
        if ionly:
            params["config"] = {"ionly": True},
        return self.network._rpc.content_create(params)

    def update_follow_up(self, followup_post, content):
        """update a follow-up on a post

        :param followup_post: json of the follow up post
        :param content: content of the follow up post
        :return: if the follow up post was successful updated
        """
        self.network.update_post(followup_post, content)

    def get_post(self, cid):
        """ retrieve data for a certain post

        :param cid: cid of the post of you want to retrieve data for
        :return: if the post update was successful
        """
        return self.network.get_post(cid)

    def get_post_from_db(self, cid):
        """ retrieve data from the db for a certain post

        :param cid: cid of the post of you want to retrieve data for
        :return: Mongo result object
        """
        query = {"cid": cid}
        return self.DB_manger.find(query)

    def mark_as_duplicate(self, duplicated_cid, master_cid, msg='Piazza bot found this Duplicate'):
        """ make the given post as duplicate of another

        :param duplicated_cid: cid of the post of you want to make as duplicate
        :param master_cid: cid of the post of you want to put the duplicate under
        :param msg: msg for why the post is marked as a duplicate
        :return: if the duplicate mark request was successful
        """
        self.network.mark_as_duplicate(duplicated_cid, master_cid, msg)

    def delete_post(self, cid):
        """ delete a post from piazza

        :param cid: cid of the post of you want to delete
        :return: if the delete request was successful
        """
        self.network.delete_post(cid)

    def delete_post_db(self, cid):
        """ delete a post from the db

        :param cid: cid of the post of you want to delete
        :return: Mongo result object
        """
        return self.DB_manger.del_by_cid(cid)

    def get_piazza_suggestions(self, query):
        params = {"nid": self.class_id, "query": query}
        r = self.network._rpc.request(method="network.find_similar", data=params)
        return self.network._rpc._handle_error(r, "Could not get suggestions {}.".format(repr(params)))


sch = sched.scheduler(time.time, time.sleep)
bot = None
def run_bot_site_querey(sc):
   print("running at 100 mins")
   bot.heart_beat()
   bot.generate_embeddings()
   bot.heart_beat()
   print("done sequence")
   sch.enter(6000, 1, run_bot_site_querey, (sc,))


if __name__ == "__main__":
    # corpus = r"C:\Users\sohai\Documents\Uni 2020\csc392\piazzabot\data\corpus.plk"
    login = np.loadtxt(r"C:\Users\karlc\Documents\ut\_y4\CSC492\login.txt", dtype=str)

    bot = PiazzaBot(login[0], login[1], "kg9odngyfny6s9")

    print(bot.get_post(17))
    print(bot.get_piazza_suggestions("When will we get out marks back <p>I am wondering when we will get our A1 marks back</p>"))
    #query: "When will we get out marks back <p>I am wondering when we will get our A1 marks back</p>"
    sch.enter(6, 1, run_bot_site_querey, (sch,))
    sch.run()







