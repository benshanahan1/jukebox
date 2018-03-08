from flask_restful import Resource
from flask import request, session, abort
from spotify import Client
from lib.utilities import recreate_client_from_session, get_user_id


class Me(Resource):
    """Read-only info about current user.
    """
    def get(self):
        me = session.get("me")
        return me if me else {}


class Party(Resource):
    """Party resource.

    Create or obtain details about a pre-existing party.
    """
    def get(self, party_name):
        """ Anyone can access details about a party. """
        # TODO database call
        return "You accessed the party: {}".format(party_name)

    def post(self, party_name):
        """ Create a new party. User must be authenticated and have a stored session. """
        client          = recreate_client_from_session()
        user_id         = get_user_id()
        party_details   = request.get_json()
        if client and user_id:
            # Create the playlist.
            new_playlist_metadata = client.api.user_playlist_create(
                user_id,
                party_details["name"],
                description=party_details["description"])
            new_playlist_id = new_playlist_metadata["id"]

            ## Get the tracklist in URIs for the submitted starter playlist.
            # First, get the URI and parse out the playlist ID. The ID is the
            # last bit after ``playlist:``:
            #
            #       spotify:user:spotify:playlist:37i9dQZF1DX4JAvHpjipBk
            #                    ^ user_id        ^ playlist ID
            starter_playlist_uri        = party_details["playlist"]
            starter_playlist_user_id    = starter_playlist_uri.split(":")[2]
            starter_playlist_id         = starter_playlist_uri.split(":")[4]

            # Now, retrieve the playlist's tracks from Spotify's API.
            received_data = client.api.user_playlist_tracks(starter_playlist_user_id, 
                starter_playlist_id)
            starter_playlist_tracks = [item["track"]["uri"] for item in received_data["items"]]

            # Add the entire tracklist from the starter playlist to the new playlist.
            client.api.user_playlist_tracks_add(user_id, 
                new_playlist_id, starter_playlist_tracks)

            # Add the party and itself details into the database.
            # TODO add database call

            return "Created new party: {}".format(party_name)
        else:
            abort(401, "User has not logged in to Spotify.")


class Votes(Resource):
    """Enable user voting (without login required).
    """
    def get(self, party_name, song_id, vote_type):
        vote_type = vote_type.lower()
        # TODO database calls
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