from django.core.urlresolvers import reverse

def get_username(session):
    lfmSession = session.get('lfmSession')
    if lfmSession:
        return lfmSession['name']

def connect(session, lastfmApp, token):
    lfmSession = lastfmApp.auth.get_session(str(token))
    session['lfmSession'] = lfmSession

def get_auth_url(request, lastfmApp):
    return lastfmApp.auth.get_url('http://' + request.get_host() + reverse('connect_lastfm'))

def is_connected(session):
    return session.has_key('lfmSession')

def disconnect(session):
    if is_connected(session):
        del session['lfmSession']

