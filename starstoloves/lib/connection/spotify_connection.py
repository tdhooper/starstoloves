from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth, SpotifyOauthError

from starstoloves import settings
from .connection import ConnectionHelper


class SpotifyConnectionHelper(ConnectionHelper):

    def __init__(self, user, token=None, **kwargs):
        self.user = user
        self.token = token
        super().__init__(**kwargs)

    def connect(self, response_code, redirect_uri):
        auth = SpotifyOAuth(
            client_id=settings.SPOTIFY['client_id'],
            client_secret=settings.SPOTIFY['client_secret'],
            redirect_uri=redirect_uri,
        )
        try:
            token_response = auth.get_access_token(response_code)
            self.token = token_response['access_token']
            sp = Spotify(auth=self.token)
            self.username = sp.me()['id']
            self.state = self.CONNECTED
        except SpotifyOauthError:
            self.state = self.FAILED

        self.repository.save(self)
