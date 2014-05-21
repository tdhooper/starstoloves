from django.core.urlresolvers import reverse

def _get_session_context(lfmSession):
    return {
        'lfmUsername': lfmSession['name'],
        'lfmDisconnectUrl': reverse('disconnect_lastfm'),
    }

def _get_connect_context():
    return {
        'lfmConnectUrl': reverse('connect_lastfm')
    }

def negotiate_connection(session, context):
    lfmSession = session.get('lfmSession')
    if lfmSession:
        context.update(_get_session_context(lfmSession))
    else:
        context.update(_get_connect_context())

def is_connected(session):
    return session.has_key('lfmSession')
