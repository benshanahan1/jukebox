from flask_restful import Resource
from flask import request, session, abort, redirect, url_for
from spotify import OAuth, Client
from configparser import ConfigParser

# Load configuration files.
app_config = ConfigParser()
app_config.read("config/app.cfg")

# Server configuration.
HOST        = app_config["APP"]["host"]
PORT        = app_config["APP"].getint("port")
FULL_HOST   = "http://{}:{}".format(HOST, PORT)


def get_client():
    token = session.get("spotify_token")
    if not token:
        return redirect(url_for("login"))
    client = Client(get_auth(token))
    return client

def get_auth(token=None):
    auth = OAuth(
        app_config["SPOTIFY_AUTH"]["client_id"],
        app_config["SPOTIFY_AUTH"]["client_secret"],
        redirect_uri="{}/{}".format(FULL_HOST, app_config["SPOTIFY_AUTH"]["local_redirect_uri"]),
        scopes=app_config["SPOTIFY_AUTH"]["scopes"].split(",")
    )
    auth.token = token
    return auth




class SpotifyAuthorize(Resource):
    """
    """
    def get(self):
        auth = get_auth()
        return redirect(auth.authorize_url)

class SpotifyCallback(Resource):
    """
    """
    def get(self):
        error_message = request.args.get("error")
        if error_message == "access_denied":
            abort(401, "User declined Spotify account access.")
        elif error_message is not None:
            abort(404, "Request failed: {}".format(error_message))
        auth = get_auth()
        auth.request_token(request.url)
        session["spotify_token"] = auth.token
        # global client
        client = get_client()
        return redirect(url_for("jukebox_app"))




class Me(Resource):
    """
    """
    def get(self):
        client = get_client()
        return client.api.me()

class Party(Resource):
    """
    """
    def get(self, party_name):
        return "{}!".format(party_name)

    def post(self, party_name):
        party_details   = request.get_json()
        client          = get_client()
        me              = client.api.me()
        user_id         = me["id"]
        if user_id:

            # Create the playlist.
            new_playlist_metadata = client.api.user_playlist_create(
                user_id,
                party_details["name"],
                description=party_details["description"])
            new_playlist_id = new_playlist_metadata["id"]

            # Add some songs to the playlist.
            client.api.user_playlist_tracks_add(user_id, new_playlist_id, 
                ["spotify:track:2mKz2YoxA65ZPzTv3i5s0A",
                "spotify:track:6wnAP0sHeZcHMXyjFfMqDL",
                "spotify:track:1j2xBvnfvDnxScznDyS2gV",
                "spotify:track:4uDxy3hQqjVx9CA28EOWht"])

            # print("request returned: {}".format(rv))

            # GET /v1/users/{user_id}/playlists/{playlist_id} Get a Playlist

            # client.api.user_playlist_tracks_add(user_id, )

            return "Successfully created new party: {}".format(party_name)
        else:
            abort(401, "User has not logged in to Spotify.")


class Song(Resource):
    """
    """
    def get(self, party_name, song_id):
        return "Song with id {}".format(song_id)

    def post(self, party_name, song_id):
        return "Added new song with id {}".format(song_id)


class Votes(Resource):
    """
    """
    def get(self, party_name, song_id, vote_type):
        vote_type = vote_type.lower()
        if vote_type == "up":
            return "Upvote count for {}".format(song_id)
        elif vote_type == "down":
            return "Downvote count for {}".format(song_id)
        elif vote_type == "all":
            return "Total vote count for {}".format(song_id)
        else:
            return "Unrecognized vote type."

    def put(self, party_name, song_id, vote_type):
        return "Voting {} for song {}".format(vote_type, song_id)