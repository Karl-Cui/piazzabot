from flask import Flask, render_template, make_response
from flask import jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from bot.piazza_code import PiazzaBot
import numpy as np

app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={"/api/*": {"origins": "*"}})
login = np.loadtxt(r"C:\Users\sohai\Documents\Uni 2020\csc392\login.txt", dtype=str)
bot = PiazzaBot(login[0], login[1], "kg9odngyfny6s9")

def make_bot_page(header, msg):
    """
    Make simple html page out of the given header and msg

    :param header: header for the the html page
    :param msg: the content of the html page body
    :return: HTML page
    """
    html = "<html> <head> <title>Piazza Bot</title> </head> <body> <h1>{}</h1> <p>{}</p></body></html>".format(header, msg)
    return html


class PostPublic(Resource):

    def get(self, cid):
        """
        mark the given post as public

        :param cid: cid of the post to make public
        :return: HTML page
        """
        result = bot.get_post_from_db(cid)
        headers = {'Content-Type': 'text/html'}
        if result is None:
            return make_response(make_bot_page('error', 'current post cid={} is invalid'.format(cid)), 200, headers)

        if result["is_marked"]:
            mark_id = result["mark_id"]
            bot.update_follow_up(mark_id, "Piazza Bot Has Processed this post")
            bot.update_post(result["cid"], result["type"], result["revision"], result["folders"],
                            result["subject"], result["content"], True)

        return make_response(make_bot_page('Processed post with cid={}'.format(cid), 'The post has now been make public for everyone to see'), 200, headers)


class MarkDuplicate(Resource):
    def get(self, post_cid, master_cid):
        """
        delete the given post by its cid since its a duplicate of the master cid post

        :param post_cid: cid of the post to delete
        :param master_cid: cid of the post that the current one is a duplicate of
        :return: HTML page
        """
        result = bot.get_post_from_db(post_cid)
        headers = {'Content-Type': 'text/html'}
        if result is None:
            return make_response(make_bot_page('error', 'current post cid={} is invalid'.format(post_cid)), 200, headers)
        bot.delete_post(post_cid)
        print(bot.delete_post_db(post_cid))

        msg = 'the post has been deleted please refer to post <a href="https://piazza.com/class/kg9odngyfny6s9?cid={}" target="_blank" rel="noopener"> @{}</a> its duplicate'.format(master_cid, master_cid)

        return make_response(make_bot_page('Processed post with cid={} as a duplicate'.format(post_cid), msg),200,headers)


class MarkFollowUp(Resource):

    def get(self, post_cid, master_cid):
        """
        mark the given post as a of the master cid post

        :param post_cid: cid of the post to make into a follow up
        :param master_cid: cid of the post that the current one is a similar too
        :return: HTML page
        """
        result = bot.get_post_from_db(post_cid)
        headers = {'Content-Type': 'text/html'}
        if result is None:
            return make_response(make_bot_page('error', 'current post cid is invalid'),200,headers)

        follow_up = '<p>{}</p> <p>{}</p>'.format(result["subject"], result['content'])
        bot.create_piazza_bot_follow_up(master_cid, follow_up)
        bot.delete_post(post_cid)
        print(bot.delete_post_db(post_cid))

        msg = 'the post has now been moved to being a followup under post <a href="https://piazza.com/class/kg9odngyfny6s9?cid={}" target="_blank" rel="noopener"> @{}</a>'.format(master_cid, master_cid)
        return make_response(make_bot_page('Processed post with cid={} as follow up'.format(post_cid), msg),200,headers)


api.add_resource(PostPublic, '/api/post/<string:cid>')
api.add_resource(MarkDuplicate, "/api/dup/<string:post_cid>/<string:master_cid>")
api.add_resource(MarkFollowUp, "/api/followup/<string:post_cid>/<string:master_cid>")

if __name__ == '__main__':
    app.run(debug=True)
