from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from starstoloves import middleware
from starstoloves import forms
from helpers import spotify_connection

def lastfm_connection_ui_context(request):
    if request.lastfm_connection.is_connected():
        context = {
            'lfmUsername': request.lastfm_connection.get_username(),
            'lfmDisconnectUrl': reverse('disconnect_lastfm'),
        }
    else:
        context = {
            'lfmConnectUrl': reverse('connect_lastfm'),
        }
    if request.lastfm_connection.get_connection_state() is request.lastfm_connection.FAILED:
        context.update({
            'lfmConnectFailure': True
        })
    return context

def spotify_connection_form(request):
    if request.method == 'POST':
        form = forms.SpotifyConnectForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            request.spotify_connection.connect(username)
            if request.spotify_connection.get_connection_state() is request.spotify_connection.FAILED:
                form.set_connection_error()
        return form
    return forms.SpotifyConnectForm()

def spotify_connection_ui_context(request, form):
    if request.spotify_connection.is_connected():
        return {
            'spUsername': request.spotify_connection.get_username(),
            'spDisconnectUrl': reverse('disconnect_spotify'),
        }
    return {
        'spForm': form,
        'spConnectUrl': reverse('index'),
    }

def index(request):
    context = {}
    session = request.session

    context.update(lastfm_connection_ui_context(request))

    if request.lastfm_connection.is_connected():
        form = spotify_connection_form(request)
        context.update(spotify_connection_ui_context(request, form))

    if request.spotify_connection.is_connected():
        spSession = session.get('spSession')
        if spSession and spSession['userUri']:
            def get_tracks(item):
                return {
                    'name': item.track.load().name,
                    'date': item.create_time,
                }
            
            user = request.spotify_session.get_user(spSession['userUri'])
            starred = user.load().starred
            tracks = starred.load().tracks_with_metadata
            context['starred'] = map(get_tracks, tracks)

    return render_to_response('index.html', context_instance=RequestContext(request, context))

def connectLastfm(request):
    if request.lastfm_connection.is_connected():
        return redirect(reverse('index'))
    token = request.GET.get('token')
    if token:
        request.lastfm_connection.connect(token)
        return redirect(reverse('index'))
    callback_url = request.build_absolute_uri(reverse('connect_lastfm'))
    auth_url = request.lastfm_connection.get_auth_url(callback_url)
    return redirect(auth_url)

def disconnectLastfm(request):
    request.lastfm_connection.disconnect()
    return redirect(reverse('index'))

def disconnectSpotify(request):
    request.spotify_connection.disconnect()
    return redirect(reverse('index'))
    