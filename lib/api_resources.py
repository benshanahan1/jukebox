from flask_restful import Resource
from flask import request, session, abort
from spotify import Client
from lib.utilities import get_database_connection
from lib.utilities import recreate_client_from_session, get_user_id
from lib.utilities import generate_party_id
from re import sub

database = get_database_connection()

class Me(Resource):
    """Read-only info about current user.
    """
    def get(self):
        me = session.get("me")
        return me if me else {}


class Party(Resource):
    def get(self, party_id):
        """Get details about a party.
        """
        if party_id and len(party_id) > 0:
            if database.check_party_exists(party_id):
                party_id = sub(r"\W+", "", party_id)  # clean string
                return database.get_party(party_id)
            else:
                abort(404, "The party could not be found.")
        else:
            abort(404, "Invalid party specified.")

    def delete(self, party_id):
        """Delete a party and remove it from the database. This action requires
        that the logged in user is also the party host.
        """
        client  = recreate_client_from_session()
        user_id = get_user_id()
        if client and user_id:
            if database.is_user_party_host(user_id, party_id):
                database.delete_party(party_id)
                return {"message": "Successfully deleted party {}.".format(party_id)}
            else:
                abort(403, "User is not the party host.")
        else:
            abort(403, "User is not logged in to spotify.")


class CreateParty(Resource):
    """Create a new party via POST request.
    """
    def post(self):
        """ Create a new party. User must be authenticated and have a stored session. """
        client          = recreate_client_from_session()
        user_id         = get_user_id()
        party_details   = request.get_json()
        if client and user_id:
            # Create the playlist.
            party_name              = party_details["name"]
            party_description       = party_details["description"]
            party_starter_playlist  = party_details["playlist"]
            # new_playlist_metadata   = client.api.user_playlist_create(
            #     user_id,
            #     party_name,
            #     description=party_description)
            # new_playlist_id = new_playlist_metadata["id"]

            ## Get the tracklist in URIs for the submitted starter playlist.
            # First, get the URI and parse out the playlist ID. The ID is the
            # last bit after ``playlist:``:
            #
            #       spotify:user:spotify:playlist:37i9dQZF1DX4JAvHpjipBk
            #                    ^ user_id        ^ playlist ID
            if party_starter_playlist:
                starter_playlist_user_id    = party_starter_playlist.split(":")[2]
                starter_playlist_id         = party_starter_playlist.split(":")[4]

                # Now, retrieve the playlist's tracks from Spotify's API.
                received_data = client.api.user_playlist_tracks(starter_playlist_user_id, 
                    starter_playlist_id)
                tracks = [item["track"] for item in received_data["items"]]
                # uris   = [track["uri"] for track in tracks]
            else:
                tracks = []

            # Add the entire tracklist from the starter playlist to the new playlist.
            # client.api.user_playlist_tracks_add(user_id, new_playlist_id, uris)

            # Add the party and itself details into the database.
            party_id = generate_party_id()
            database.create_party(user_id, client.auth.token, 
                party_id, party_name, party_description, party_starter_playlist, tracks)

            return {
                "party_id": party_id,
                "message": "Created new party: {}".format(party_details["name"])
            }
        else:
            abort(403, "User has not logged in to Spotify.")


class Votes(Resource):
    """Enable user voting (without login required).
    """
    def get(self, party_id, song_id):
        """ Retrieve total vote count for a song. """
        if database.check_song_exists(party_id, song_id):
            return database.get_total_votes(party_id, song_id)
        else:
            abort(404, "Specified song / party does not exist.")

    def post(self, party_id, song_id):
        """ Up-vote a song. """
        if database.check_song_exists(party_id, song_id):
            vote_key  = "%s%s".format(party_id, song_id)
            prev_vote = session.get(vote_key)
            if not prev_vote or prev_vote == "down":
                # this value is either None, down, or up. Only allow up-vote if None or down.
                if database.add_vote(party_id, song_id, 1):
                    session[vote_key] = "up"
                    msg = "Up-voted song {}.".format(song_id)
                else:
                    msg = "Failed to up-vote song."
            else:
                msg = "Cannot up-vote same song twice."
            return {
                "message":    msg,
                "vote_count": database.get_total_votes(party_id, song_id)
            }
        else:
            abort(404, "Specified song / party does not exist.")

    def delete(self, party_id, song_id):
        """ Down-vote a song. """
        if database.check_song_exists(party_id, song_id):
            vote_key  = "%s%s".format(party_id, song_id)
            prev_vote = session.get(vote_key)
            if not prev_vote or prev_vote == "up":
                # this value is either None, down, or up. Only allow down-vote if None or up.
                if database.add_vote(party_id, song_id, -1):
                    session[vote_key] = "down"
                    msg = "Down-voted song {}.".format(song_id)
                else:
                    msg = "Failed to down-vote song."
            else:
                msg = "Cannot down-vote same song twice."
            return {
                "message":    msg,
                "vote_count": database.get_total_votes(party_id, song_id)
            }
        else:
            abort(404, "Specified song / party does not exist.")





# TODO: make votes adjust the playlist in spotify.


# # If it's an unknown user or non-host user, let's recreate the host
# # Spotify authorization so we can interact with the Web API.
# token = database.retrieve_spotify_token(party_id)
# if token:
#     client = recreate_client(token)
#     if client:
#         print("got client")
#     else:
#         print("didn't work?")