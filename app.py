#!/usr/bin/python3

from gevent.wsgi import WSGIServer
from flask import Flask, session, request, redirect, url_for, render_template
from flask_restful import Api
from spotify import Client, OAuth
from lib.api_resources import Me, Party, Song, Votes
from json import load
from flask_session import Session


# Load configuration from file.
with open("config/app.json") as config_file:
    app_config = load(config_file)

# Server configuration.
HOST        = app_config["APP"]["host"]
PORT        = app_config["APP"]["port"]
API_ROOT    = "{}/{}".format(app_config["APP"]["api_base"], app_config["APP"]["api_version"])
FULL_HOST   = "http://{}:{}".format(HOST, PORT)

# Set up the app.
app                 = Flask(__name__)
api                 = Api(app)
http_server         = WSGIServer((HOST, PORT), app)
app.config["SECRET_KEY"] = app_config["APP"]["secret_key"]

# Use Flask-Session to enable file-system session storage, and permit saving
# entire objects from memory.
SESSION_TYPE            = "filesystem"
SESSION_PERMANENT       = False
SESSION_FILE_DIR        = "session_cache"
SESSION_FILE_THRESHOLD  = 500
app.config.from_object(__name__)
Session(app)

# Add API resources.
api.add_resource(Me,    API_ROOT + "/me")
api.add_resource(Party, API_ROOT + "/party/<string:party_name>")
api.add_resource(Song,  API_ROOT + "/party/<string:party_name>/song/<string:song_id>")
api.add_resource(Votes, API_ROOT + "/party/<string:party_name>/song/<string:song_id>/votes/<string:vote_type>")



###############################################################################
## Helper functions.
###############################################################################

def get_context(include_dict=None):
    # Template context for displayed pages.
    context = {
        "app_name":             app_config["APP"]["app_name"],
        "app_version":          app_config["APP"]["app_version"],
        "app_description":      app_config["APP"]["app_description"],
        "app_author":           app_config["APP"]["app_author"],
        "app_author_website":   app_config["APP"]["app_author_website"]
    }
    if include_dict:
        context = {**context, **include_dict}  # merge dictionaries
    return context


def get_auth(token=None):
    auth = OAuth(
        app_config["SPOTIFY_AUTH"]["client_id"],
        app_config["SPOTIFY_AUTH"]["client_secret"],
        redirect_uri="{}/{}".format(FULL_HOST, app_config["SPOTIFY_AUTH"]["local_redirect_uri"]),
        scopes=app_config["SPOTIFY_AUTH"]["scopes"].split(",")
    )
    auth.token = token
    return auth


###############################################################################
## Flask routes.
###############################################################################

@app.route("/")
@app.route("/welcome")
def welcome():
    return render_template("welcome.html", context=get_context())


@app.route("/jukebox")
def jukebox_app():
    # Create a Spotify Client and store its parameters in a persistent session.
    token                       = session.get("spotify_token")
    client                      = Client(get_auth(token))
    session["client_session"]   = client.session
    session["me"]               = client.api.me()
    party_code  = request.args.get("party")
    if not party_code:
        if not token:
            return redirect(url_for("authorize"))
        else:
            return render_template("jukebox_create_party.html", context=get_context())
    else:
        if True:  #TODO: does_party_exist(party_code)
            # TODO get info based on party code
            # TODO if a token exists, determine if logged in user owns this party.
            additional_context = {
                "is_party_host":    True,  # is_party_host(user_id, party_code)
                "party_code":       party_code
            }
            return render_template("jukebox_view_party.html", context=get_context(additional_context))


@app.route("/login")
@app.route("/authorize")
def authorize():
    auth = get_auth()
    return redirect(auth.authorize_url)


@app.route("/callback")
def callback():
    error_message = request.args.get("error")
    if error_message == "access_denied":
        abort(401, "User declined Spotify account access.")
    elif error_message is not None:
        abort(404, "Request failed: {}".format(error_message))
    auth = get_auth()
    auth.request_token(request.url)
    session["spotify_token"] = auth.token
    return redirect(url_for("jukebox_app"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("welcome"))



if __name__ == "__main__":
    http_server.serve_forever()