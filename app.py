#!/usr/bin/python3

from gevent.wsgi import WSGIServer
from flask import Flask, session, redirect, url_for, render_template
from flask_restful import Api
from spotify import OAuth, Client
from lib.api_resources import Me, Party, Song, Votes
from lib.api_resources import SpotifyAuthorize, SpotifyCallback
from configparser import ConfigParser

# Load configuration files.
app_config = ConfigParser()
app_config.read("config/app.cfg")

# Server configuration.
HOST        = app_config["APP"]["host"]
PORT        = app_config["APP"].getint("port")
API_ROOT    = "{}/{}".format(app_config["APP"]["base_url"], app_config["APP"]["api_version"])

# Set up the app.
app                 = Flask(__name__)
api                 = Api(app)
http_server         = WSGIServer((HOST, PORT), app)
app.config["SECRET_KEY"] = app_config["APP"]["secret_key"]

# Add API resources.
api.add_resource(Me,    API_ROOT + "/me")
api.add_resource(Party, API_ROOT + "/party/<string:party_name>")
api.add_resource(Song,  API_ROOT + "/party/<string:party_name>/song/<string:song_id>")
api.add_resource(Votes, API_ROOT + "/party/<string:party_name>/song/<string:song_id>/votes/<string:vote_type>")
api.add_resource(SpotifyAuthorize,  API_ROOT + "/spotify/authorize")
api.add_resource(SpotifyCallback,   API_ROOT + "/spotify/callback")

def get_context():
    return {
        "app_name":             app_config["APP"]["app_name"],
        "app_version":          app_config["APP"]["app_version"],
        "app_description":      app_config["APP"]["app_description"],
        "app_author":           app_config["APP"]["app_author"],
        "app_author_website":   app_config["APP"]["app_author_website"]
    }

@app.route("/")
@app.route("/welcome")
def welcome():
    return render_template("welcome.html", context=get_context())

@app.route("/jukebox")
def jukebox_app():
    token = session.get("spotify_token")
    if not token:
        return redirect(url_for("login"))
    return render_template("jukebox.html", context=get_context())

@app.route("/login")
def login():
    return redirect(API_ROOT + "/spotify/authorize")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("welcome"))


if __name__ == "__main__":
    http_server.serve_forever()