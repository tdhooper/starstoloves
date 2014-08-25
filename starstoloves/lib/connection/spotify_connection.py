import spotify

from .connection import ConnectionHelper, MissingUserError
from starstoloves.models import SpotifyConnection

class SpotifyConnectionHelper(ConnectionHelper):

    connection_name = 'spotify_connection'
    connection_class = SpotifyConnection

    def __init__(self, user, session):
        self.user = user
        self.session = session

    def get_user_uri(self):
        return self._get_from_connection('user_uri')

    def connect(self, username):
        if not self.user:
            raise MissingUserError()

        user_uri = 'spotify:user:' + username
        # for now the only way I know of validating a user exists is to try and load a playlist
        connection, created = SpotifyConnection.objects.get_or_create(user=self.user)
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

