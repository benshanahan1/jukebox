from flask_restful import Resource


class Party(Resource):
    """
    """
    def get(self, party_name):
        return "{}!".format(party_name)

    def post(self, party_name):
        return "Created new party playlist: {}".format(party_name)


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