#!/usr/bin/python3

from gevent.wsgi import WSGIServer
from flask import Flask, redirect, request, abort, session, url_for, jsonify, render_template
from flask_restful import Api
from spotify import OAuth, Client
from api_resources import Party, Song, Votes
from configparser import ConfigParser

# Load configuration files.
app_config = ConfigParser()
app_config.read("app.cfg")

# Server configuration.
HOST        = app_config["APP"]["host"]
PORT        = app_config["APP"].getint("port")
API_ROOT    = "{}/{}".format(
    app_config["APP"]["base_url"], app_config["APP"]["version"])
if PORT != 80:
    FULL_HOST = "http://{}:{}".format(HOST, PORT)
else:
    FULL_HOST = "http://{}".format(HOST)

# Set up the app.
app = Flask(__name__)
app.config["SECRET_KEY"] = app_config["APP"]["secret_key"]
api = Api(app)
http_server = WSGIServer((HOST, PORT), app)

# Get ready for Spotify OAuth authentication.
spotify_client_id       = app_config["SPOTIFY_AUTH"]["client_id"]
spotify_client_secret   = app_config["SPOTIFY_AUTH"]["client_secret"]
spotify_scopes          = app_config["SPOTIFY_AUTH"]["scopes"].split(",")
spotify_redirect_uri    = "{}/{}".format(
    FULL_HOST, app_config["SPOTIFY_AUTH"]["local_redirect_uri"])

# Add API resources.
api.add_resource(Party, API_ROOT + "/party/<string:party_name>")
api.add_resource(Song,  API_ROOT + "/party/<string:party_name>/song/<string:song_id>")
api.add_resource(Votes, API_ROOT + "/party/<string:party_name>/song/<string:song_id>/votes/<string:vote_type>")

def get_auth(token=None):
    auth = OAuth(
        spotify_client_id,
        spotify_client_secret,
        redirect_uri=spotify_redirect_uri,
        scopes=spotify_scopes
    )
    auth.token = token
    return auth

@app.route("/")
@app.route("/welcome")
def welcome():
    return render_template("welcome.html", context={})

@app.route("/jukebox")
def jukebox_app():
    token = session.get("spotify_token")
    if not token:
        return redirect(url_for("authorize"))
    client = Client(get_auth(token))
    
    # Extract user information from call to Web API.
    user                = client.api.me()
    user_id             = user["id"]
    user_display_name   = user["display_name"]
    user_image          = user["images"][0]["url"]
    user_uri            = user["uri"]

    # client.api.user_playlist_create(user_id, "jukebox_test_playlist",
    #     description="Jukebox test playlist.")

    return render_template("jukebox.html", context={
        "user":                 user,
        "user_id":              user_id,
        "user_display_name":    user_display_name,
        "user_image":           user_image,
        "user_uri":             user_uri
    })

@app.route("/authorize")
def authorize():
    auth = get_auth()
    return redirect(auth.authorize_url)

@app.route("/callback")
def callback():
    error_message = request.args.get("error")
    if error_message == "access_denied":
        return "User declined Spotify account access."
    elif error_message is not None:
        return "Request failed: {}".format(error_message)

    auth = get_auth()
    auth.request_token(request.url)
    session["spotify_token"] = auth.token
    return redirect(url_for("jukebox_app"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    http_server.serve_forever()