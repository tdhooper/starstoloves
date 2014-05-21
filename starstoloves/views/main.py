from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.http import HttpResponse
from django.utils.decorators import decorator_from_middleware

import spotify

from starstoloves import forms
from starstoloves import middleware


def get_lastfm_session_context(lfmSession):
    return {
        'lfmUsername': lfmSession['name'],
        'lfmDisconnectUrl': reverse(disconnectLastfm),
    }

def get_lastfm_connect_context():
    return {
        'lfmConnectUrl': reverse(connectLastfm)
    }

def negotiate_lastfm_connection(session, context):
    lfmSession = session.get('lfmSession')
    if lfmSession:
        context.update(get_lastfm_session_context(lfmSession))
    else:
        context.update(get_lastfm_connect_context())

def is_lastfm_connected(session):
    return session.has_key('lfmSession')



def get_spotify_session_context(spSession):
    return {
        'spUsername': spSession['username'],
        'spDisconnectUrl': reverse(disconnectSpotify),
    }

def get_spotify_connect_context(form):
    return {
        'spForm': form,
        'spConnectUrl': reverse(index),
    }

def negotiate_spotify_connection(request, context):
    spSession = request.session.get('spSession')
    if spSession:
        context.update(get_spotify_session_context(spSession))
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
                context.update(get_spotify_session_context(spSession))
                request.session['spSession'] = spSession
            else:
                context.update(get_spotify_connect_context(form))
        else:
            form = forms.SpotifyConnectForm(spotifySession=request.spotifySession);
            context.update(get_spotify_connect_context(form))

def is_spotify_connected(session):
    return session.has_key('spSession')



@decorator_from_middleware(middleware.SpotifySession)
@decorator_from_middleware(middleware.LastfmApp)
def index(request):
    context = {}

    session = request.session

    negotiate_lastfm_connection(session, context)
    negotiate_spotify_connection(request, context)

    if is_lastfm_connected(session):
        context['showSpotifyForm'] = True

    if is_spotify_connected(session):
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
    if is_lastfm_connected(request.session):
        return redirect(reverse(index))
    token = request.GET.get('token')
    if token:
        session = request.lastfmApp.auth.get_session(str(token))
        request.session['lfmSession'] = session
        return redirect(reverse(index))
    authUrl = request.lastfmApp.auth.get_url('http://' + request.get_host() + reverse(connectLastfm))
    return redirect(authUrl)

def disconnectLastfm(request):
    if is_lastfm_connected(request.session):
        del request.session['lfmSession']
    return redirect(reverse(index))

def disconnectSpotify(request):
    if is_spotify_connected(request.session):
        del request.session['spSession']
    return redirect(reverse(index))
    