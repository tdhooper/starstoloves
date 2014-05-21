from django.core.urlresolvers import reverse
from starstoloves import forms

def _get_session_context(spSession):
    return {
        'spUsername': spSession['username'],
        'spDisconnectUrl': reverse('disconnect_spotify'),
    }

def _get_connect_context(form):
    return {
        'spForm': form,
        'spConnectUrl': reverse('index'),
    }

def negotiate_connection(request, context):
    spSession = request.session.get('spSession')
    if spSession:
        context.update(_get_session_context(spSession))
    else:
        if request.method == 'POST':
            form = forms.SpotifyConnectForm(request.POST, spotifySession=request.spotifySession);
            if form.is_valid():
                userUri = form.cleaned_data.get('userUri')
                user = request.spotifySession.get_user(userUri)
                username = user.load().display_name
                spSession = {
                    'username': username,
                    'userUri': userUri,
                }
                context.update(_get_session_context(spSession))
                request.session['spSession'] = spSession
            else:
                context.update(_get_connect_context(form))
        else:
            form = forms.SpotifyConnectForm(spotifySession=request.spotifySession);
            context.update(_get_connect_context(form))

def is_connected(session):
    return session.has_key('spSession')

def disconnect(session):
    if is_connected(session):
        del session['spSession']