from .connection import ConnectionHelper

from django.core.urlresolvers import reverse

class LastfmConnectionHelper(ConnectionHelper):

    def __init__(self, session_storage, app):
        super(LastfmConnectionHelper, self).__init__(session_storage)
        self.app = app

    def _get_session_key(self):
        return 'lastfm_connection'

    def get_username(self):
        session = self._get_session()
        return session.get('name')

    def get_auth_url(self, callback_url):
        return self.app.auth.get_url(callback_url)

    def connect(self, token):
        try:
            app_session = self.app.auth.get_session(str(token))
            session = self._get_session()
            session.update(app_session)
            self._set_state(self.CONNECTED)
        except:
            self._set_state(self.FAILED)