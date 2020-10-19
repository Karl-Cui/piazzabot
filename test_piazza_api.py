from piazza_api import Piazza


def get_question(post):
    return post["history"][0]["content"]


with open(r"C:\Users\karlc\Documents\login.txt", "r") as f:
    email = f.readline()
    password = f.readline()

p = Piazza()
p.user_login(email=email, password=password)
user_profile = p.get_user_profile()

csc420 = p.network("k9ish8q5xos7b4")

# posts = mat344.iter_all_posts(limit=50)
# for post in posts:
#     get_question(post)

csc420.create_post()


