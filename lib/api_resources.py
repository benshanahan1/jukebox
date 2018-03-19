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

    def post(self, party_id):
        # Export the specified party to Spotify. If the export_playlist field 
        # from the database is populated and still exists in Spotify, just 
        # update this playlist. Otherwise, create a new playlist.
        client  = recreate_client_from_session()
        user_id = get_user_id()
        if not user_id or not client:
            abort(403, "User is not logged in to Spotify.")

        if database.check_party_exists(party_id):
            if database.is_user_party_host(user_id, party_id):
                # Okay, we're authenticated and everything exists.
                # Retrieve party details from database.
                details = database.get_party(party_id)
                if not details:
                    return {
                        "message": "Unable to get information about the party from database!",
                        "success": False
                    }

                prev_playlist = database.get_party_exported_playlist(party_id)
                if prev_playlist and prev_playlist != "none":
                    old_playlist_id = prev_playlist.split(":")[4]
                    result = client.api.me_unfollow_playlist(user_id, old_playlist_id)

                # Create a new playlist using name and description from database.
                playlist = client.api.user_playlist_create(user_id,
                    details["meta"]["party_name"],
                    description=details["meta"]["party_description"])
                playlist_id = playlist["id"]
                database.update_party_exported_playlist(party_id, 
                    "spotify:user:{}:playlist:{}".format(user_id, playlist_id))

                # Sort and reorder song_uris by song_votes, descending.
                song_votes  = [song["votes"] for song in details["songs"]]
                song_uris   = ["spotify:track:{}".format(song["song_id"]) for song in details["songs"]]
                sorted_idx  = sorted(range(len(song_votes)), key=lambda k: song_votes[k], reverse=True)
                sorted_uris = [song_uris[i] for i in sorted_idx]
                # Add songs from database to the new playlist.
                client.api.user_playlist_tracks_add(user_id, playlist_id, sorted_uris)

                return {
                    "message": "Successfully exported party to Spotify.",
                    "success": True
                }
            else:
                abort(403, "User is not party host.")
        else:
            abort(404, "Party does not exist.")

    def delete(self, party_id):
        """Delete a party and remove it from the database. This action requires
        that the logged in user is also the party host.
        """
        client  = recreate_client_from_session()
        user_id = get_user_id()
        if client and user_id:
            if database.is_user_party_host(user_id, party_id):
                database.delete_party(party_id)
                return {
                    "message": "Successfully deleted party {}.".format(party_id),
                    "success": True
                }
            else:
                abort(403, "User is not the party host.")
        else:
            abort(403, "User is not logged in to Spotify.")


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
            else:
                tracks = []

            # Add the party and itself details into the database.
            party_id = generate_party_id()
            database.create_party(user_id, party_id, party_name, party_description, 
                party_starter_playlist, tracks)

            return {
                "party_id": party_id,
                "message": "Created new party: {}".format(party_details["name"])
            }
        else:
            abort(403, "User has not logged in to Spotify.")


class UpdateParty(Resource):
    """Update name and or description of a party.
    """
    def post(self):
        user_id         = get_user_id()
        party_details   = request.get_json()
        if user_id:
            msg = ""
            party_id = party_details["party_id"]
            if "name" in party_details:
                new_name = party_details["name"]
                database.update_party_name(party_id, new_name)
                msg += "Updated party name to '{}'. ".format(new_name)
            if "description" in party_details:
                new_description = party_details["description"]
                database.update_party_description(party_id, new_description)
                msg += "Updated party description to '{}'. ".format(new_description)
            if "name" not in party_details and "description" not in party_details:
                abort(400, "Bad data payload.")
            return { "message": msg, "success": True }
        else:
            abort(403, "User has not logged in to Spotify.")


class Song(Resource):
    """ Add a song to a party. Requires user authorization.
    """
    def post(self, party_id, song_uri):
        client  = recreate_client_from_session()
        user_id = get_user_id()
        if user_id:
            try:
                song_id = song_uri.split(":")[2]
            except:
                abort(400, "Invalid song URI.")
            track = client.api.track(song_id)
            if database.add_song_to_party(party_id, song_id, track):
                return {
                    "message": "Added song {} to party {}.".format(song_id, party_id),
                    "success": True
                }
            else:
                return {
                    "message": "Specified party does not exist.",
                    "success": False
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
            vote_key  = "{}{}".format(party_id, song_id)
            prev_vote = session.get(vote_key)
            if not prev_vote or prev_vote == "down":
                # this value is either None, down, or up. Only allow up-vote if None or down.
                if not prev_vote:
                    rv = database.add_vote(party_id, song_id, 1)
                elif prev_vote == "down":
                    rv = database.add_vote(party_id, song_id, 2)
                if rv:
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
            vote_key  = "{}{}".format(party_id, song_id)
            prev_vote = session.get(vote_key)
            if not prev_vote or prev_vote == "up":
                # this value is either None, down, or up. Only allow up-vote if None or up.
                if not prev_vote:
                    rv = database.add_vote(party_id, song_id, -1)
                elif prev_vote == "up":
                    rv = database.add_vote(party_id, song_id, -2)
                if rv:
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