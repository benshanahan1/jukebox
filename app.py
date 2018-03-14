# !/usr/bin/python3

from gevent.wsgi import WSGIServer
from flask import Flask, session, request, redirect, url_for, render_template
from flask_restful import Api
from spotify import Client, OAuth
from lib.api_resources import Me, Party, CreateParty, Votes
from lib.utilities import get_database_connection, get_user_id
from lib.utilities import get_server_location, get_app_secret_key, get_api_root, get_jinja_context
from lib.utilities import get_spotify_auth, store_client_in_session, recreate_client_from_session
from json import load
from flask_session import Session

# Set up the app.
app         = Flask(__name__)
api         = Api(app)
http_server = WSGIServer(get_server_location(), app)
app.config["SECRET_KEY"] = get_app_secret_key()
database    = get_database_connection()

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
api.add_resource(Me, API_ROOT + "/me")
api.add_resource(CreateParty, API_ROOT + "/party")
api.add_resource(Party, API_ROOT + "/party/<string:party_id>")
api.add_resource(Votes, API_ROOT + "/party/<string:party_id>/song/<string:song_id>/votes")


###############################################################################
## Flask routes.
###############################################################################

@app.route("/")
@app.route("/welcome")
def welcome():
    return render_template("welcome.html", context=get_jinja_context())


@app.route("/jukebox")
def jukebox_create_party():
    token = session.get("spotify_token")  # retrieve authorized spotify token, if exists
    # We are *creating* a new party.
    if not token:
        # We don't have a valid token stored. User is not authorized. 
        # Redirect to Spotify for authorization.
        return redirect(url_for("authorize"))
    else:
        # We have a token, let's authorize the token with Spotify and then
        # store the client in a session so we can access it later. Then
        # render the create party page.
        client = recreate_client_from_session()
        store_client_in_session(client)  # store client in session so we can later retrieve it
        return render_template("jukebox_create_party.html", 
            context=get_jinja_context())

@app.route("/<string:party_id>")
def jukebox_view_party(party_id):
    token = session.get("spotify_token")  # retrieve authorized spotify token, if exists
    user_id = get_user_id()  # get user_id from session ,if exists
    if party_id and database.check_party_exists(party_id):
        # We are *viewing* an existing party. Check if the current user is 
        # logged in, and if so, if they are the party host.
        party_details = database.get_party(party_id)
        highlight     = request.args.get("highlight")
        additional_context = {
            "party_id":             party_id,
            "party_name":           party_details["meta"]["party_name"],
            "party_description":    party_details["meta"]["party_description"],
            "tracks":               party_details["songs"],
            "is_party_host":        database.is_user_party_host(user_id, party_id),
            "highlight":            highlight
        }
        return render_template("jukebox_view_party.html", context=get_jinja_context(additional_context))
    else:
        return render_template("jukebox_party_does_not_exist.html", context=get_jinja_context())


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
    return redirect(url_for("jukebox_create_party"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("welcome"))



if __name__ == "__main__":
    http_server.serve_forever()