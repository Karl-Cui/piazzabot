from piazza_api import Piazza
from piazza_api.rpc import PiazzaRPC
import numpy as np


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

def update_post(network, post, post_type, post_folders, post_subject, post_content, visibility_all=True, is_announcement=0, bypass_email=0, anonymous=False):
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
    try:
        cid = post["id"]
    except KeyError:
        cid = post


    params = {
        "cid": cid,
        "subject": post_subject,
        "content": post_content,
        "folders": post_folders,
        "type": post_type,
        "revision": 4,
        "visibility" : "all" if visibility_all else "instr_kg9odngyfny6s9,itf8rrur21a73b"
    }
    print(params)
    return network._rpc.content_update(params)

p = Piazza()

login = np.loadtxt(r"C:\Users\sohai\Documents\Uni 2020\csc392\login.txt", dtype=str)
p.user_login(login[0], login[1])

user_profile = p.get_user_profile()

test108 = p.network("kg9odngyfny6s9")

my_post = test108.get_post(7)

#test108.create_instructor_answer(my_post, "<p>jk i know how to use this thing i was just playing</p>", 1)

#test108.create_followup(my_post, "<p>hi I am also very lost!!!!</p>")

#create_private_post(test108, "question", ["general"], "this meant for only the instructors", "<p> hello fellow instructors </p>")

update_post(test108, my_post, "question", ["general"], " trying to make sure its public!!", "<p> hello fellow world</p>")

print(my_post)







