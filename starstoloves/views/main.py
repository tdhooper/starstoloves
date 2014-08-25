import json
import re

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError

from starstoloves.lib.user.spotify_user import SpotifyUser
from starstoloves.lib.user.user import starred_track_searches
from .connection import connection_index_decorator, connection_index_processor

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

@connection_index_decorator
def index(request):
    context = {}
    if request.lastfm_connection.is_connected() and request.spotify_connection.is_connected():
        context['tracks'] = get_tracks_data(request)
    return render_to_response('index.html', context_instance=RequestContext(request, context, [connection_index_processor]))

def result_update(request):
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
    