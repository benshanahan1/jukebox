#!/usr/bin/python3

from gevent.wsgi import WSGIServer
from flask import Flask
from flask_restful import Api
from api_resources import Party, Song, Votes

HOST        = "0.0.0.0"
PORT        = 5000
API_ROOT    = "/api/v1"

app = Flask(__name__)
api = Api(app)
http_server = WSGIServer((HOST, PORT), app)

# Add API resources.
api.add_resource(Party, API_ROOT + "/party/<string:party_name>")
api.add_resource(Song,  API_ROOT + "/party/<string:party_name>/song/<string:song_id>")
api.add_resource(Votes, API_ROOT + "/party/<string:party_name>/song/<string:song_id>/votes/<string:vote_type>")

@app.route("/")
def index():
    return "OK"


if __name__ == "__main__":
    http_server.serve_forever()