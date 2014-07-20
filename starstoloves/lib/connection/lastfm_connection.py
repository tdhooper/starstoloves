from .connection import ConnectionHelper, MissingUserError
from starstoloves.models import LastfmConnection

class LastfmConnectionHelper(ConnectionHelper):

    def __init__(self, user, app):
        self.user = user
        self.app = app

    def get_username(self):
        if (self.user):
            try: 
                return self.user.lastfm_connection.username
            except LastfmConnection.DoesNotExist:
                pass
        return None

    def get_connection_state(self):
        if (self.user):
            try:
                return self.user.lastfm_connection.state
            except LastfmConnection.DoesNotExist:
                pass
        return self.DISCONNECTED

    def get_auth_url(self, callback_url):
        return self.app.auth.get_url(callback_url)

    def connect(self, token):
        if not self.user:
            raise MissingUserError()
            
        connection = LastfmConnection(user=self.user)
        try:
            app_session = self.app.auth.get_session(str(token))
            connection.username = app_session['name']
            connection.state = self.CONNECTED
        except:
            connection.state = self.FAILED
        connection.save()

    def disconnect(self):
        try: 
            self.user.lastfm_connection.delete()
        except:
            pass
