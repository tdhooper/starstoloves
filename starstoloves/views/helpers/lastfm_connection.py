from django.core.urlresolvers import reverse

class LastfmConnectionHelper:

    def __init__(self, session, lastfmApp):
        self.session = session
        self.lastfmApp = lastfmApp

    def get_username(self):
        lfmSession = self.session.get('lfmSession')
        if lfmSession:
            return lfmSession['name']

    def connect(self, token):
        lfmSession = self.lastfmApp.auth.get_session(str(token))
        self.session['lfmSession'] = lfmSession

    def get_auth_url(self, request):
        return self.lastfmApp.auth.get_url('http://' + request.get_host() + reverse('connect_lastfm'))

    def is_connected(self):
        return self.session.has_key('lfmSession')

    def disconnect(self):
        if self.is_connected():
            del self.session['lfmSession']

