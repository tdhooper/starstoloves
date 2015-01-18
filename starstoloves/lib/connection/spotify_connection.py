from spotipy import Spotify
from spotipy.oauth2 import SpotifyOauthError

from .connection import ConnectionHelper


class SpotifyConnectionHelper(ConnectionHelper):

    def __init__(self, user, auth, token=None, **kwargs):
        self.user = user
        self.auth = auth
        self.token = token
        super().__init__(**kwargs)

    def connect(self, response_code):
        try:
            token_response = self.auth.get_access_token(response_code)
            self.token = token_response['access_token']
            sp = Spotify(auth=self.token)
            self.username = sp.me()['id']
            self.state = self.CONNECTED
        except SpotifyOauthError:
            self.state = self.FAILED

        self.repository.save(self)
