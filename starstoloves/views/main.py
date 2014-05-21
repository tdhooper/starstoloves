from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.decorators import decorator_from_middleware

from starstoloves import middleware
from helpers import lastfm_connection
from helpers import spotify_connection

@decorator_from_middleware(middleware.SpotifySession)
@decorator_from_middleware(middleware.LastfmApp)
def index(request):
    context = {}

    session = request.session

    lastfm_connection.negotiate_connection(session, context)
    spotify_connection.negotiate_connection(request, context)

    if lastfm_connection.is_connected(session):
        context['showSpotifyForm'] = True

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
    if lastfm_connection.is_connected(request.session):
        return redirect(reverse('index'))
    token = request.GET.get('token')
    if token:
        session = request.lastfmApp.auth.get_session(str(token))
        request.session['lfmSession'] = session
        return redirect(reverse('index'))
    authUrl = request.lastfmApp.auth.get_url('http://' + request.get_host() + reverse('connect_lastfm'))
    return redirect(authUrl)

def disconnectLastfm(request):
    if lastfm_connection.is_connected(request.session):
        del request.session['lfmSession']
    return redirect(reverse('index'))

def disconnectSpotify(request):
    if spotify_connection.is_connected(request.session):
        del request.session['spSession']
    return redirect(reverse('index'))
    