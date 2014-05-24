from django.core.urlresolvers import reverse
import spotify

class SpotifyConnectionHelper:

    DISCONNECTED = 0;
    CONNECTED = 1;
    FAILED = 2;

    def __init__(self, session, spotify_session):
        self.session = session
        self.spotify_session = spotify_session

    def get_username(self):
        spSession = self.session.get('spSession')
        if spSession:
            return spSession['username']

    def get_user_uri(self):
        spSession = self.session.get('spSession')
        if spSession:
            return spSession['userUri']

    def connect(self, username):
        userUri = 'spotify:user:' + username
        # for now the only way I know of validating a user exists is to try and load a playlist
        if username:
            user = self.spotify_session.get_user(userUri)
            starred = user.load().starred
            try:
                tracks = starred.load().tracks_with_metadata
                self.session['spSession'] = {
                    'username': username,
                    'userUri': userUri,
                }
                if 'sp_connection_failed' in self.session:
                    del self.session['sp_connection_failed']
            except spotify.Error:
                self.session['sp_connection_failed'] = True

    def get_connection_state(self):
        if 'spSession' in self.session:
            return self.CONNECTED
        elif 'sp_connection_failed' in self.session:
            return self.FAILED
        return self.DISCONNECTED

    def is_connected(self):
        return self.get_connection_state() is self.CONNECTED

    def disconnect(self):
        if 'spSession' in self.session:
            del self.session['spSession']