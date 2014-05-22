from django.core.urlresolvers import reverse

class LastfmConnectionHelper:

    DISCONNECTED = 0;
    CONNECTED = 1;
    FAILED = 2;

    def __init__(self, session, lastfmApp):
        self.session = session
        self.lastfmApp = lastfmApp

    def get_username(self):
        lfmSession = self.session.get('lfmSession')
        if lfmSession:
            return lfmSession['name']

    def connect(self, token):
        try:
            lfmSession = self.lastfmApp.auth.get_session(str(token))
            self.session['lfmSession'] = lfmSession
            if 'lfm_connection_failed' in self.session:
                del self.session['lfm_connection_failed']
        except:
            self.session['lfm_connection_failed'] = True

    def get_auth_url(self, callback_url):
        return self.lastfmApp.auth.get_url(callback_url)

    def get_connection_state(self):
        if 'lfmSession' in self.session:
            return self.CONNECTED
        elif 'lfm_connection_failed' in self.session:
            return self.FAILED
        return self.DISCONNECTED

    def is_connected(self):
        return self.get_connection_state() is self.CONNECTED

    def disconnect(self):
        if 'lfmSession' in self.session:
            del self.session['lfmSession']

