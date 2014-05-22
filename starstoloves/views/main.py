from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.decorators import decorator_from_middleware

from starstoloves import middleware
from helpers.lastfm_connection import LastfmConnectionHelper
from helpers import spotify_connection

@decorator_from_middleware(middleware.LastfmApp)
@decorator_from_middleware(middleware.SpotifySession)
def index(request):
    context = {}
    session = request.session
    lastfm_connection = LastfmConnectionHelper(session, request.lastfmApp)

    if lastfm_connection.is_connected():
        context['lfmUsername'] = lastfm_connection.get_username()
        context['lfmDisconnectUrl'] = reverse('disconnect_lastfm')
        context['showSpotifyForm'] = True
    else:
        context['lfmConnectUrl'] = reverse('connect_lastfm')

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

@decorator_from_middleware(middleware.LastfmApp)
def connectLastfm(request):
    lastfm_connection = LastfmConnectionHelper(request.session, request.lastfmApp)
    if lastfm_connection.is_connected():
        return redirect(reverse('index'))
    token = request.GET.get('token')
    if token:
        lastfm_connection.connect(token)
        return redirect(reverse('index'))
    return redirect(lastfm_connection.get_auth_url(request))

@decorator_from_middleware(middleware.LastfmApp)
def disconnectLastfm(request):
    lastfm_connection = LastfmConnectionHelper(request.session, request.lastfmApp)
    lastfm_connection.disconnect()
    return redirect(reverse('index'))

def disconnectSpotify(request):
    spotify_connection.disconnect(request.session)
    return redirect(reverse('index'))
    