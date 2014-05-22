from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.decorators import decorator_from_middleware

from starstoloves import middleware
from helpers import spotify_connection

@decorator_from_middleware(middleware.LastfmApi)
@decorator_from_middleware(middleware.SpotifySession)
def index(request):
    context = {}
    session = request.session

    if request.lastfm_connection.is_connected():
        context['lfmUsername'] = request.lastfm_connection.get_username()
        context['lfmDisconnectUrl'] = reverse('disconnect_lastfm')
        context['showSpotifyForm'] = True
    else:
        context['lfmConnectUrl'] = reverse('connect_lastfm')

    if request.lastfm_connection.get_connection_state() is request.lastfm_connection.FAILED:
        context['lfmConnectFailure'] = True

    spotify_connection.negotiate_connection(request, context)

    if spotify_connection.is_connected(session):
        spSession = session.get('spSession')
        if spSession and spSession['userUri']:
            def get_tracks(item):
                return {
                    'name': item.track.load().name,
                    'date': item.create_time,
                }
            
            user = request.spotifySession.get_user(spSession['userUri'])
            starred = user.load().starred
            tracks = starred.load().tracks_with_metadata
            context['starred'] = map(get_tracks, tracks)

    return render_to_response('index.html', context_instance=RequestContext(request, context))

@decorator_from_middleware(middleware.LastfmApi)
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

@decorator_from_middleware(middleware.LastfmApi)
def disconnectLastfm(request):
    request.lastfm_connection.disconnect()
    return redirect(reverse('index'))

def disconnectSpotify(request):
    spotify_connection.disconnect(request.session)
    return redirect(reverse('index'))
    