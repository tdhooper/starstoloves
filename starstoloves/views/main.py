import json
import re

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseServerError

from starstoloves import forms
from starstoloves.lib.user.spotify_user import SpotifyUser
from starstoloves.lib.user.user import starred_track_searches

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

def get_searches(request):
    sp_user = SpotifyUser(request.session_user, request.spotify_session, request.spotify_connection)
    return starred_track_searches(sp_user, request.lastfm_app)

def get_tracks_data(request):
    return [
        {
            'track_name': search['track']['track_name'],
            'artist_name': search['track']['artist_name'],
            # 'date_saved': track.date_saved,
            'date_saved': 0,
            'id': search['query'].id,
            'status': search['query'].status,
            'results': search['query'].results
        }
        for search in get_searches(request)
    ]

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
        context['tracks'] = get_tracks_data(request)

    return render_to_response('index.html', context_instance=RequestContext(request, context))

def resultUpdate(request):
    if request.spotify_connection.is_connected():
        tracks = get_tracks_data(request)
        status_by_id = {
            re.search('status\[(.+)\]', key).groups()[0]: value
            for key, value in request.POST.items()
        }
        if status_by_id:
            tracks = [
                track
                for track in tracks
                if
                    not track['id'] in status_by_id
                    or track['status'] != status_by_id[track['id']]
            ]
        results = [
            {
                'id': track['id'],
                'status': track['status'],
                'html': render(request, 'result.html', {'track': track}).content.decode("utf-8"),
            }
            for track in tracks
        ]
        return HttpResponse(json.dumps(results), content_type="application/json")
    return HttpResponse('No results', status=401)

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
    return redirect('index')
    