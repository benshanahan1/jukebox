#!/usr/bin/python3

import spotipy
import spotipy.util as util
from random import randint
from sys import argv, exit
from configparser import ConfigParser

scope = 'user-library-read playlist-modify-public playlist-modify-private'

if len(argv) > 1:
    username = argv[1]
else:
    print("Usage: {} username".format(argv[0]))
    exit()

config = ConfigParser()
config.read("spotify_credentials.keys")

token = util.prompt_for_user_token(username, scope,
    client_id=config["Spotify"]["client_id"],
    client_secret=config["Spotify"]["client_secret"],
    redirect_uri=config["Spotify"]["redirect_uri"])

if token:
    sp = spotipy.Spotify(auth=token)
    
    # testing
    is_public = False
    new_playlist_metadata = sp.user_playlist_create(
        user=username, 
        name="test_{}".format(randint(0,10000)), 
        public=is_public,
        description="Jukebox playlist.")
    new_playlist_id = new_playlist_metadata["id"]
    
    print("Created {} playlist {}".format(
        "public" if is_public else "private", new_playlist_id))

    # rename or add description
    # sp.user_playlist_change_details(username, new_playlist_id, 
    #     description="Jukebox playlist.")
    
    # add some songs to it
    sp.user_playlist_add_tracks(username, new_playlist_id, 
        ["spotify:track:2mKz2YoxA65ZPzTv3i5s0A",
        "spotify:track:6wnAP0sHeZcHMXyjFfMqDL",
        "spotify:track:1j2xBvnfvDnxScznDyS2gV",
        "spotify:track:4uDxy3hQqjVx9CA28EOWht"])

    print("Press ENTER to remove song")
    input()

    # remove a track
    sp.user_playlist_remove_all_occurrences_of_tracks(username, new_playlist_id,
        ["spotify:track:4uDxy3hQqjVx9CA28EOWht"])

    print("Press ENTER to reorder song in position 2 to beginning of playlist")
    input()

    # reorder playlist
    sp.user_playlist_reorder_tracks(username, new_playlist_id,
        2, 0)


else:
    print("Can't get token for", username)