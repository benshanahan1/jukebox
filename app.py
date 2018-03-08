# !/usr/bin/python3

from gevent.wsgi import WSGIServer
from flask import Flask, session, request, redirect, url_for, render_template
from flask_restful import Api
from spotify import Client, OAuth
from lib.api_resources import Me, Party, Song, Votes
from lib.utilities import get_server_location, get_app_secret_key, get_api_root, get_jinja_context
from lib.utilities import get_spotify_auth, store_client_in_session
from json import load
from flask_session import Session

# Set up the app.
app         = Flask(__name__)
api         = Api(app)
http_server = WSGIServer(get_server_location(), app)
app.config["SECRET_KEY"] = get_app_secret_key()

# Use Flask-Session to enable file-system session storage, and permit saving
# entire objects from memory.
SESSION_TYPE            = "filesystem"
SESSION_PERMANENT       = False
SESSION_FILE_DIR        = "session_cache"
SESSION_FILE_THRESHOLD  = 500
app.config.from_object(__name__)
Session(app)

# Add API resources.
API_ROOT = get_api_root() 
api.add_resource(Me,    API_ROOT + "/me")
api.add_resource(Party, API_ROOT + "/party/<string:party_name>")
api.add_resource(Song,  API_ROOT + "/party/<string:party_name>/song/<string:song_id>")
api.add_resource(Votes, API_ROOT + "/party/<string:party_name>/song/<string:song_id>/votes/<string:vote_type>")


###############################################################################
## Flask routes.
###############################################################################

@app.route("/")
@app.route("/welcome")
def welcome():
    return render_template("welcome.html", context=get_jinja_context())


@app.route("/jukebox")
def jukebox_app():
    # Create a Spotify Client and store its parameters in a persistent session.
    token   = session.get("spotify_token")
    client  = Client(get_spotify_auth(token))
    store_client_in_session(client)  # store client in session so we can later retrieve it
    party_code  = request.args.get("party")
    if not party_code:
        if not token:
            return redirect(url_for("authorize"))
        else:
            return render_template("jukebox_create_party.html", context=get_jinja_context())
    else:
        if True:  #TODO: does_party_exist(party_code)
            # TODO get info based on party code
            # TODO if a token exists, determine if logged in user owns this party.
            additional_context = {
                "is_party_host":    True,  # is_party_host(user_id, party_code)
                "party_code":       party_code
            }
            return render_template("jukebox_view_party.html", context=get_jinja_context(additional_context))


@app.route("/login")
@app.route("/authorize")
def authorize():
    auth = get_spotify_auth()
    return redirect(auth.authorize_url)


@app.route("/callback")
def callback():
    error_message = request.args.get("error")
    if error_message == "access_denied":
        abort(401, "User declined Spotify account access.")
    elif error_message is not None:
        abort(404, "Request failed: {}".format(error_message))
    auth = get_spotify_auth()
    auth.request_token(request.url)
    session["spotify_token"] = auth.token
    return redirect(url_for("jukebox_app"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("welcome"))



if __name__ == "__main__":
    http_server.serve_forever()