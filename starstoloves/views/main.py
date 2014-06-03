from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from starstoloves import forms
from starstoloves.views.helpers import spotify_connection
from starstoloves.lib.search import LastfmSearchWithLoves
from starstoloves.lib.track import SearchingTrack

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
            else:
                form.connection_success = True
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

def get_starred_tracks(request):
    tracks = []
    user_uri = request.spotify_connection.get_user_uri()
    user = request.spotify_session.get_user(user_uri)
    starred = user.load().starred
    playlist = starred.load().tracks_with_metadata
    for item in playlist:
        track = item.track.load()
        tracks.append({
            'track_name': track.name,
            'artist_name': track.artists[0].load().name,
            'date_saved': item.create_time,
        })
    return tracks

def get_loved_tracks_urls(request):
    if 'loved_tracks_urls' in request.session:
        return request.session['loved_tracks_urls']
    username = request.lastfm_connection.get_username()
    loved_tracks_response = request.lastfm_app.user.get_loved_tracks(username)
    urls = [track['url'] for track in loved_tracks_response['track']]
    request.session['loved_tracks_urls'] = urls
    return urls

def forget_loved_tracks_urls(request):
    if 'loved_tracks_urls' in request.session:
        del request.session['loved_tracks_urls']

def get_searching_tracks_data(request, searcher):
    tracks = []
    tracks_data = request.session.get('tracks_data', False)
    if not tracks_data:
        starred_tracks = get_starred_tracks(request)
        for track in starred_tracks:
            tracks.append(SearchingTrack(track['track_name'], track['artist_name'], track['date_saved'], searcher))
    else:
        tracks = [
            SearchingTrack(track['track_name'], track['artist_name'], track['date_saved'], searcher, track['search'])
            for track in tracks_data
        ]
    tracks_data = [track.data for track in tracks]
    request.session['tracks_data'] = tracks_data
    return tracks_data

def forget_searching_tracks_data(request):
    if 'tracks_data' in request.session:
        del request.session['tracks_data']

def index(request):
    context = {}
    session = request.session

    context.update(lastfm_connection_ui_context(request))

    if request.lastfm_connection.is_connected():
        form = spotify_connection_form(request)
        if form.connection_success:
            # Stop double POST on refresh
            return redirect('index')
        context.update(spotify_connection_ui_context(request, form))

    if request.spotify_connection.is_connected():
        loved_tracks_urls = get_loved_tracks_urls(request)
        searcher = LastfmSearchWithLoves(request.lastfm_app, loved_tracks_urls)
        context['tracks'] = get_searching_tracks_data(request, searcher)

    return render_to_response('index.html', context_instance=RequestContext(request, context))

def connectLastfm(request):
    if request.lastfm_connection.is_connected():
        return redirect('index')
    token = request.GET.get('token')
    if token:
        request.lastfm_connection.connect(token)
        return redirect('index')
    callback_url = request.build_absolute_uri(reverse('connect_lastfm'))
    auth_url = request.lastfm_connection.get_auth_url(callback_url)
    return redirect(auth_url)

def disconnectLastfm(request):
    request.lastfm_connection.disconnect()
    forget_loved_tracks_urls(request)
    return redirect('index')

def disconnectSpotify(request):
    request.spotify_connection.disconnect()
    forget_searching_tracks_data(request)
    return redirect('index')
    