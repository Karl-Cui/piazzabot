from flask import Flask
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


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

class PostPublic(Resource):
    def get(self, cid):
        result = bot.get_post_from_db(cid)
        if result is None:
            {'error': 'cid is invalid'}

        if result["is_marked"]:
            mark_id = result["mark_id"]
            bot.update_follow_up(mark_id, "Piazza Bot Has Processed this post")
            bot.update_post(result["cid"], result["type"], result["revision"], result["folders"],
                            result["subject"], result["content"], True)


        return {'hello': 'world'}

api.add_resource(HelloWorld, '/')
api.add_resource(PostPublic, '/api/post/<string:cid>')


if __name__ == '__main__':
    app.run(debug=True)
