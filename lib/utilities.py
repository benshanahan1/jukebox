"""App utility functions.
"""
from spotify import OAuth, Client
from flask import session
from json import load
from lib.database import Database
from uuid import uuid4

# Load app configuration from ``config_json_file`` file. Do this on load.
def load_app_config(config_json_file):
    """ Load app configuration from file. """
    with open(config_json_file) as config_file:
        app_config = load(config_file)
    return app_config
app_config = load_app_config("config/app.json")

###############################################################################
## Connect to database.
###############################################################################
def get_database_connection():
    database = Database(
        app_config["DATABASE"]["host"],
        app_config["DATABASE"]["username"],
        app_config["DATABASE"]["password"],
        app_config["DATABASE"]["dbname"])
    return database

###############################################################################
## Server and API helper functions.
###############################################################################

def get_server_location():
    return (app_config["APP"]["host"], app_config["APP"]["port"])

def get_app_secret_key():
    return app_config["APP"]["secret_key"]

def get_api_root():
    return "{}/{}".format(
        app_config["APP"]["api_base"], app_config["APP"]["api_version"])

def get_jinja_context(include_dict=None):
    """ Template context for displayed pages. """
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

###############################################################################
## Spotify Web API, auth, and client management functions.
###############################################################################

def get_spotify_auth(token=None):
    auth = OAuth(
        app_config["SPOTIFY_AUTH"]["client_id"],
        app_config["SPOTIFY_AUTH"]["client_secret"],
        redirect_uri="{}/{}".format(
            "http://{}:{}".format(*get_server_location()),
            app_config["SPOTIFY_AUTH"]["local_redirect_uri"]),
        scopes=app_config["SPOTIFY_AUTH"]["scopes"].split(",")
    )
    auth.token = token
    return auth

def store_client_in_session(client):
    """ Store Client object into session so we can retrieve it later. """
    session["client_session"]       = client.session
    me                              = client.api.me()
    session["me"]                   = me
    session["user_id"]              = me["id"]
    session["user_display_name"]    = me["display_name"]

def recreate_client_from_session():
    """ Attempt to recreate Client from values stored in session. """
    token = session.get("spotify_token")
    if token:
        auth = get_spotify_auth(token)
        return Client(auth, session.get("client_session"))
    else:
        return None

def get_user_id():
    """ Return user's Spotify ID if there is a user logged in. """
    user_id = session.get("user_id")
    return user_id if user_id else None

def get_user_display_name():
    """ Return user's display name if there is a user logged in. """
    user_display_name = session.get("user_display_name")
    return user_display_name if user_display_name else None

###############################################################################
## Party creation and management.
###############################################################################

def generate_party_id():
    ID_LENGTH = 6
    return uuid4().hex[:ID_LENGTH]