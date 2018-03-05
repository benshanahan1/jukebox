class SpotifyInterface(object):

    def __init__(self):
        self.app_scope = """
            user-library-read
            playlist-modify-public
            playlist-modify-private
            """

        # Connect app to Spotify.
        self.config = ConfigParser()
        self.config.read("spotify_credentials.keys")
        self.token = util.prompt_for_user_token(username, scope,
            client_id=config["Spotify"]["client_id"],
            client_secret=config["Spotify"]["client_secret"],
            redirect_uri=config["Spotify"]["redirect_uri"])