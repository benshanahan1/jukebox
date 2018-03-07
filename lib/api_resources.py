from flask_restful import Resource
from flask import request, session, abort
from spotify import Client, OAuth


class Me(Resource):
    """
    """
    def get(self):
        me = session.get("me")
        return me if me else {}

class Party(Resource):
    """
    """
    def get(self, party_name):
        return "{}!".format(party_name)

    def post(self, party_name):
        party_details   = request.get_json()
        auth            = OAuth(None, None)
        auth.token      = session.get("spotify_token")
        client          = Client(auth, session.get("client_session"))
        me              = session.get("me")
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