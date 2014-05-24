# TODO: Move this into a separate process
# or use https://docs.djangoproject.com/en/dev/ref/applications/#django.apps.AppConfig.ready

import spotify
import settings
from lib import spotify_auth
import __builtin__

def run():
    config = spotify.Config()
    config.user_agent = settings.SPOTIFY['user_agent']
    config.load_application_key_file(settings.SPOTIFY['key_file'])
    sp_session = spotify.Session(config=config)

    auth = spotify_auth.SpotifyAuth(sp_session);
    username = settings.SPOTIFY['username']
    password = settings.SPOTIFY['password']
    success = auth.login(username, password)

    if success:
        __builtin__.spotify_session = sp_session