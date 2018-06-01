# Jukebox

Crowd-source the playlist for your next party.

**Disclaimer**: this app only uses the Spotify Web API, so without some form of hack, it's near-impossible to modify the queue. Therefore, this app just lets people vote on songs in a playlist and then rearranges the playlist so that the most popular songs come first. This revised playlist needs to be manually re-exported to Spotify before it can be listened to. I built this app to explore the Spotify Web API and it's pretty useless for as long as Spotify disallows real-time queue modification. Jukebox does, however, let anonymous users vote on song priority in a playlist, so that's kind of cool.

## Installation

```shell
sudo pip3 install config/requirements.txt
cp config/app.cfg.generic config/app.cfg
```

Then modify the contents of 'config/app.cfg'. You will need to specify a client secret (for the Flask server), your MySQL database host, password, etc., and your [Spotify Client ID and secret](https://developer.spotify.com/my-applications/).

You must also set the following **Redirect URI** in your Spotify App console, verbatim: `http://<ip-address>:<port>/callback`

IP and port should match those specified in your 'config/app.cfg' file.

Once everything is installed and configured, run:

```shell    
python3 app.py
```

And navigate to the site in your web browser.



## TODO

* timeout and error on API queries from front-end that fail or hang



## Screenshots

![Welcome](static/img/screenshot/welcome-page.png "Welcome")

![Spotify login](static/img/screenshot/spotify-login-page.png "Spotify login")

![Jukebox app](static/img/screenshot/jukebox-app-page.png "Jukebox app")

![Playlist created](static/img/screenshot/spotify-playlist-created.png "Playlist created")
