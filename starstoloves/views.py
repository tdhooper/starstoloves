from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.http import HttpResponse
from django.utils.decorators import decorator_from_middleware
import forms
import middleware
import spotify

def lastfm_connection_processor(request):
    lfmSession = request.session.get('lfmSession')
    if lfmSession:
        return {
            'lfmUsername': lfmSession['name'],
            'lfmDisconnectUrl': reverse(disconnectLastfm),
        }
    return {'lfmConnectUrl': reverse(connectLastfm)}

def spotify_connection_processor(request):
    spSession = request.session.get('spSession')
    if spSession:
        return {
            'spUsername': spSession['username'],
            'spDisconnectUrl': reverse(disconnectSpotify),
        }

    if request.method == 'POST':
        form = forms.SpotifyConnectForm(request.POST, spotifySession=request.spotifySession);
        if form.is_valid():
            userUri = form.cleaned_data.get('userUri')
            user = request.spotifySession.get_user(userUri)
            username = user.load().display_name
            request.session['spSession'] = {
                'username': username,
                'userUri': userUri,
            }
            return spotify_connection_processor(request)
    else:
        form = forms.SpotifyConnectForm(spotifySession=request.spotifySession);

    return {
        'spForm': form,
        'spConnectUrl': reverse(index),
    }

@decorator_from_middleware(middleware.SpotifySession)
@decorator_from_middleware(middleware.LastfmApp)
def index(request):
    context = {}

    context.update(lastfm_connection_processor(request))
    context.update(spotify_connection_processor(request))

    spSession = request.session.get('spSession')
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
    if request.session.get('lfmSession'):
        return redirect(reverse(index))
    token = request.GET.get('token')
    if token:
        session = request.lastfmApp.auth.get_session(str(token))
        request.session['lfmSession'] = session
        return redirect(reverse(index))
    authUrl = request.lastfmApp.auth.get_url('http://' + request.get_host() + reverse(connectLastfm))
    return redirect(authUrl)

def disconnectLastfm(request):
    try:
        del request.session['lfmSession']
    except KeyError:
        pass
    return redirect(reverse(index))

def disconnectSpotify(request):
    try:
        del request.session['spSession']
    except KeyError:
        pass
    return redirect(reverse(index))
    