from piazza_api import Piazza
from piazza_api.rpc import PiazzaRPC
import numpy as np
from bot.db import MongoDBManger
from Bert.basic_semantic_search import BertSemanticSearch

class PiazzaBot(object):

    def __init__(self, user, password, class_id, corpus=None, corpus_embeddings=None, default_bert=True):
        self.p = Piazza()
        self.p.user_login(user, password)
        self.user_profile = self.p.get_user_profile()
        self.network = self.p.network(class_id)
        self.DB_manger = MongoDBManger()
        self.bert = BertSemanticSearch(corpus, corpus_embeddings, default_bert)
        self.parallel_cid_list = []

    def heart_beat(self):
        posts = self.network.iter_all_posts()
        for post in posts:
            try:
                cid = post["id"]
                query = {"cid": cid}
                result = self.DB_manger.find(query)
                db_dict = self.create_db_dict(post, result)
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

            except KeyError:
                print("no cid")

    def generate_embeddings(self):
        docs = self.DB_manger.get_all()
        if docs is None:
            return 1

        corpus = []
        parallel_cid_list_local = []
        for doc in docs:
            corpus.append(doc["content"])
            parallel_cid_list_local.append(doc["cid"])

        self.bert.set_corpus(corpus)
        self.bert.preprocess_corpus()
        self.parallel_cid_list = parallel_cid_list_local


    def create_db_dict(self, post, old_post):
        try:
            cid = post["id"]
            history = post["history"]
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
                         "uid": uid,
                         "type": post_type,
                         "folders": post_folders,
                         "subject": post_subject,
                         "content": post_content,
                         "is_marked": is_marked_by_pb,
                         "mark_id": mark_id,
                         "is_processed": is_processed}
            return new_value

        except KeyError as e:
            print(e)
            return None

    def is_marked_by_piazza_bot(self, children, old_post):
        len_children = len(children)
        if len_children == 0:
            print("getting childern len 0")
            return False, False, "None"

        for follow_up in children:
            subject = follow_up['subject']
            if subject == "Piazza Bot is trying to process this post":
                return True, False, follow_up['id']
            elif subject == "Piazza Bot Has Processed this post":
                return True, True, follow_up['id']

        if old_post is not None and old_post["is_marked"]:
            return True, True, old_post["mark_id"]

        return False, False, "None"

    def make_private(self, db_dict):
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
        msg = '<p><a href="http://127.0.0.1:5000/api/post/{}" target="_blank" rel="noopener">Make Post Public</a></p>'.format(cid)

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
        try:
            uid = cur_post_content["uid"]
        except KeyError:
            uid = ""
        return uid

    def update_post(self, cid, post_type, revision, post_folders, post_subject, post_content, visibility_all=True):
        """Update a post
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
        """Create a follow-up on a post `post`.
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

    def update_follow_up(self, post, content):
        self.network.update_post(post, content)

    def get_post(self, cid):
        return self.network.get_post(cid)

    def get_post_from_db(self, cid):
        query = {"cid": cid}
        return self.DB_manger.find(query)

    def mark_as_duplicate(self, duplicated_cid, master_cid, msg='Piazza bot found this Duplicate'):
        self.network.mark_as_duplicate(duplicated_cid, master_cid, msg)

    def delete_post(self, cid):
        self.network.delete_post(cid)

    def delete_post_db(self, cid):
        return self.DB_manger.del_by_cid(cid)

if __name__ == "__main__":
    corpus = r"C:\Users\sohai\Documents\Uni 2020\csc392\piazzabot\data\corpus.plk"
    login = np.loadtxt(r"C:\Users\sohai\Documents\Uni 2020\csc392\login.txt", dtype=str)

    bot = PiazzaBot(login[0], login[1], "kg9odngyfny6s9")
    bot.heart_beat()
    bot.generate_embeddings()
    bot.heart_beat()

    print(bot.get_post(1))






