from flask import Flask, request, session, redirect, url_for, render_template, flash
from models import User, todays_recent_posts
import os   # for the secret key & nb secret key needs to be set for security of sessions/flashing etc to 
from datetime import timedelta

from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__)
app.secret_key = os.urandom(24)  


@app.route("/")
def index():
    if session.get('logged_in') == True:
        print("you are logged in")
    else:
        print('You are not logged in')
    posts = todays_recent_posts(5)
    return render_template("index.html", posts=posts)
    #render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():  #  GET retrieves remote data, and POST is used to insert/update remote data
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User(username)
        if not user.register(password):
            flash("A user with that username already exists")
        else:
            flash("You were successfully registered!")
            return redirect(url_for("login"))
        
        
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User(username)
        if not user.verify_password(password):
            flash("Invalid login!")
        else:
            flash("Successfully logged in!")
            session["username"]=user.username
            print("FFFFFFFFFFFFFFFUCKOOFFFFF", session["username"])
            print('BASTARD ', user.username)
            session['logged_in'] = True
            
            return redirect(url_for("index")) 
    return render_template("login.html")

@app.route("/add_post", methods=["POST"])
def add_post():
    title = request.form["title"]
    tags = request.form["tags"]
    text = request.form["text"]

    user = User(session["username"])

    if not title or not tags or not text:
        flash("You must give your post a title, tags, and a text body.")
    else:
        user.add_post(title, tags, text)

    return redirect(url_for("index"))


@app.route("/like_post/<post_id>")
def like_post(post_id):
    username=session.get("username")
    if not username:
        flash("you must be logged in to like a post")
        return redirect(url_for("login"))
    
    user = User(username)
    user.like_post(post_id)
    flash("Liked post")
    return redirect(request.referrer)


# @app.route("/profile/<username>")
# def profile(username):
#     user = User(username)
#     posts = user.recent_posts(5)
#     return render_template("profile.html", username=username, posts=posts)



    
# @app.route("/profile/<username>")
# def profile(username):
#     user1=User(session.get("username"))
#     user2=User(username)
#     posts=user2.recent_posts(5)
    
#     similar = []
#     if user1.username == user2.username:
#         similar = user1.similar_users(3)
        
#     return render_template("profile.html", username=username, posts=posts, similar=similar)


        
@app.route("/profile/<username>")
def profile(username):
    user1=User(session.get("username"))
    user2=User(username)
    posts=user2.recent_posts(5)
    
    similar = []
    common={}
    if user1.username == user2.username:
        similar = user1.similar_users(3)
    else:
        common = user1.commonality_of_user(user2)
        
    return render_template("profile.html", username=username, posts=posts, similar=similar, common=common)
        


@app.route("/logout")
def logout():
    session.pop("username")
    flash("Logged out")
    return redirect(url_for("index"))
