# !/usr/bin/python3

from gevent.wsgi import WSGIServer
from flask import Flask, session, request, redirect, url_for, render_template
from flask_restful import Api
from spotify import Client, OAuth
from lib.api_resources import Me, Party, CreateParty, UpdateParty, Song, Votes
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
api.add_resource(UpdateParty, API_ROOT + "/party/update")
api.add_resource(Party, API_ROOT + "/party/<string:party_id>")
api.add_resource(Song, API_ROOT + "/party/<string:party_id>/song/<string:song_uri>")
api.add_resource(Votes, API_ROOT + "/party/<string:party_id>/song/<string:song_id>/votes")


###############################################################################
## Flask routes.
###############################################################################

@app.route("/")
@app.route("/welcome")
def welcome():
    user_id = get_user_id()
    if user_id:
        return redirect(url_for("jukebox_user_account"))
    else:
        return render_template("welcome.html", context=get_jinja_context())


@app.route("/create")
def jukebox_create_party():
    user_id = get_user_id()
    # We are *creating* a new party.
    if user_id:
        return render_template("jukebox_create_party.html", context=get_jinja_context())
    else:
        # We don't have a valid token stored. User is not authorized. 
        # Redirect to Spotify for authorization.
        return redirect(url_for("welcome"))


@app.route("/<string:party_id>")
def jukebox_view_party(party_id):
    user_id = get_user_id()  # get user_id from session, if exists
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
            "is_user":              user_id is not None,
            "is_party_host":        database.is_user_party_host(user_id, party_id),
            "highlight":            highlight
        }
        return render_template("jukebox_view_party.html", context=get_jinja_context(additional_context))
    else:
        return render_template("jukebox_party_does_not_exist.html", context=get_jinja_context())


@app.route("/account")
def jukebox_user_account():
    # We are displaying the user's account details.
    user_id = get_user_id()
    if user_id:
        additional_context = {
            "user_parties": database.get_user_parties(user_id)
        }
        return render_template("jukebox_user_account.html", context=get_jinja_context(additional_context))
    else:
        return redirect("welcome")


@app.route("/login")
@app.route("/authorize")
def authorize():
    redirect_url = request.args.get("redirect")
    if redirect_url:
        session["login_redirect"] = redirect_url
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
    client = Client(auth)  # create Client object
    store_client_in_session(client)  # store in session so we can retrieve it
    redirect_url = session.get("login_redirect")
    if redirect_url:
        try:
            return redirect(redirect_url)
        except:
            pass
    return redirect(url_for("jukebox_user_account"))


@app.route("/logout")
def logout():
    redirect_url = request.args.get("redirect")
    session.clear()
    if redirect_url:
        try:
            return redirect(redirect_url)
        except:
            pass
    return redirect(url_for("welcome"))



if __name__ == "__main__":
    http_server.serve_forever()