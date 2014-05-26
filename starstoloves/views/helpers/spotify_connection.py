from .connection import ConnectionHelper

from django.core.urlresolvers import reverse
import spotify

class SpotifyConnectionHelper(ConnectionHelper):

    def __init__(self, session_storage, spotify_session):
        super(SpotifyConnectionHelper, self).__init__(session_storage)
        self.spotify_session = spotify_session

    def _get_session_key(self):
        return 'spotify_connection'

    def get_username(self):
        session = self._get_session()
        return session.get('username')

    def get_user_uri(self):
        session = self._get_session()
        return session.get('userUri')

    def connect(self, username):
        userUri = 'spotify:user:' + username
        # for now the only way I know of validating a user exists is to try and load a playlist
        if username:
            user = self.spotify_session.get_user(userUri)
            starred = user.load().starred
            try:
                tracks = starred.load().tracks_with_metadata
                session = self._get_session()
                session.update({
                    'username': username,
                    'userUri': userUri,
                })
                self._set_state(self.CONNECTED)
            except spotify.Error:
                self._set_state(self.FAILED)