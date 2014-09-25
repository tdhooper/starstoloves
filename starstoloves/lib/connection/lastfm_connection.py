from .connection import ConnectionHelper


class LastfmConnectionHelper(ConnectionHelper):

    username = None

    def __init__(self, user, app, **kwargs):
        self.user = user
        self.app = app
        super().__init__(**kwargs)

    def auth_url(self, callback_url):
        return self.app.auth.get_url(callback_url)

    def connect(self, token):
        try:
            app_session = self.app.auth.get_session(str(token))
            self.username = app_session['name']
            self.state = self.CONNECTED
        except:
            self.state = self.FAILED

        self.repository.save(self)

