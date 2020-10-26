from piazza_api import Piazza
from piazza_api.rpc import PiazzaRPC
import numpy as np
from bot.db import MongoDBManger

class PiazzaBot(object):

    def __init__(self, user, password, class_id):
        self.p = Piazza()
        self.p.user_login(user, password)
        self.user_profile = self.p.get_user_profile()
        self.network = self.p.network(class_id)
        self.DB_manger = MongoDBManger()

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
                    self.create_piazza_bot_follow_up(cid, "Piazza Bot is trying to process this post")
                    self.get_piazza_suggestions(db_dict)
                elif db_dict is not None:
                    self.DB_manger.insert_update(query, db_dict)

            except KeyError:
                print("no cid")

    def create_db_dict(self, post, old_post):
        try:
            cid = post["id"]
            history = post["history"]
            revision = len(history)
            cur_post_content = history[-1]
            uid = self.find_uid(cur_post_content)
            post_type = post["type"]
            post_folders = post['folders']
            post_subject = cur_post_content['subject']
            post_content = cur_post_content['content']
            if old_post is None:
                is_marked_by_pb, mark_id = self.is_marked_by_piazza_bot(post["children"])
            else:
                is_marked_by_pb, mark_id = old_post["is_marked"], old_post["mark_id"]
            new_value = {"cid": cid,
                         "revision": revision,
                         "uid": uid,
                         "type": post_type,
                         "folders": post_folders,
                         "subject": post_subject,
                         "content": post_content,
                         "is_marked": is_marked_by_pb,
                         "mark_id": mark_id}
            return new_value

        except KeyError as e:
            print(e)
            return None

    def is_marked_by_piazza_bot(self, children):
        len_children = len(children)
        if len_children == 0:
            return False, "None"

        for follow_up in children:
            subject = follow_up['subject']
            if subject == "Piazza Bot is trying to process this post" or subject == "Piazza Bot Has Processed this post":
                return True, follow_up['id']


    def get_piazza_suggestions(self, db_dict):
        #TODO add getting suggestions code
        try:
            if "gd6v7134AUa" != db_dict["uid"]:
                self.update_post(db_dict["cid"], db_dict["type"], db_dict["revision"], db_dict["folders"], db_dict["subject"], db_dict["content"], False)

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

    def get_post(self, cid):
        return self.network.get_post(cid)


def create_private_post(network, post_type, post_folders, post_subject, post_content, is_announcement=0, bypass_email=0, anonymous=False):
    """Create a post

    It seems like if the post has `<p>` tags, then it's treated as HTML,
    but is treated as text otherwise. You'll want to provide `content`
    accordingly.

    :param network: Network
    :type post_type: str
    :param post_type: 'note', 'question'
    :type post_folders: str
    :param post_folders: Folder to put post into
    :type post_subject: str
    :param post_subject: Subject string
    :type post_content: str
    :param post_content: Content string
    :type is_announcement: bool
    :param is_announcement:
    :type bypass_email: bool
    :param bypass_email:
    :type anonymous: bool
    :param anonymous:
    :rtype: dict
    :returns: Dictionary with information about the created post.
    """
    params = {
        "anonymous": "yes" if anonymous else "no",
        "subject": post_subject,
        "content": post_content,
        "folders": post_folders,
        "type": post_type,
        "config": {
            "bypass_email": bypass_email,
            "is_announcement": is_announcement,
            "feed_groups": "instr_kg9odngyfny6s9,itf8rrur21a73b"
        }
    }

    return network._rpc.content_create(params)

if __name__ == "__main__":
    login = np.loadtxt(r"C:\Users\sohai\Documents\Uni 2020\csc392\login.txt", dtype=str)

    bot = PiazzaBot(login[0], login[1], "kg9odngyfny6s9")
    bot.heart_beat()

    print(bot.get_post(9))






