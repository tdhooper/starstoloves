import spotify

from .connection import ConnectionHelper


class SpotifyConnectionHelper(ConnectionHelper):

    def __init__(self, user, session, user_uri=None, **kwargs):
        self.user = user
        self.session = session
        self.user_uri = user_uri
        super().__init__(**kwargs)

    def connect(self, username):
        user_uri = 'spotify:user:' + username
        # for now the only way I know of validating a user exists is to try and load a playlist
        if username:
            user = self.session.get_user(user_uri)
            starred = user.load().starred
            try:
                tracks = starred.load().tracks_with_metadata
                self.username = username
                self.user_uri = user_uri
                self.state = self.CONNECTED
            except spotify.Error:
                self.state = self.FAILED

        self.repository.save(self)

