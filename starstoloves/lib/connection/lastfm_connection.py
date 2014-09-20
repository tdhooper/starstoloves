from .connection import ConnectionHelper, MissingUserError
from starstoloves.models import LastfmConnection, User

class LastfmConnectionHelper(ConnectionHelper):

    connection_name = 'lastfm_connection'
    connection_class = LastfmConnection

    def __init__(self, user, app):
        self.user = user
        self.app = app

    def auth_url(self, callback_url):
        return self.app.auth.get_url(callback_url)

    def connect(self, token):
        if not self.user:
            raise MissingUserError()
            
        user_model = User.objects.get(session_key=self.user.session_key)
        connection = LastfmConnection(user=user_model)
        try:
            app_session = self.app.auth.get_session(str(token))
            connection.username = app_session['name']
            connection.state = self.CONNECTED
        except:
            connection.state = self.FAILED
        connection.save()

