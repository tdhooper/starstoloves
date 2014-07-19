import spotify

from .connection import DBConnectionHelper, MissingUserError
from starstoloves.models import SpotifyConnection

class SpotifyConnectionHelper(DBConnectionHelper):

    def __init__(self, user, session):
        self.user = user
        self.session = session

    def get_username(self):
        if (self.user):
            try:
                return self.user.spotify_connection.username
            except SpotifyConnection.DoesNotExist:
                pass
        return None

    def get_user_uri(self):
        if (self.user):
            try:
                return self.user.spotify_connection.user_uri
            except SpotifyConnection.DoesNotExist:
                pass
        return None

    def get_connection_state(self):
        if (self.user):
            try:
                return self.user.spotify_connection.state
            except SpotifyConnection.DoesNotExist:
                pass
        return self.DISCONNECTED

    def connect(self, username):
        if not self.user:
            raise MissingUserError()

        user_uri = 'spotify:user:' + username
        # for now the only way I know of validating a user exists is to try and load a playlist
        connection = SpotifyConnection(user=self.user)
        if username:
            user = self.session.get_user(user_uri)
            starred = user.load().starred
            try:
                tracks = starred.load().tracks_with_metadata
                connection.username = username
                connection.user_uri = user_uri
                connection.state = self.CONNECTED
            except spotify.Error:
                connection.state = self.FAILED
        connection.save()

    def disconnect(self):
        try:
            self.user.spotify_connection.delete()
        except:
            pass
