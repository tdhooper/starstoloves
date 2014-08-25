import json
import re

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError

from starstoloves.lib.user.spotify_user import SpotifyUser
from starstoloves.lib.user.lastfm_user import LastfmUser
from starstoloves.lib.user.user import starred_track_searches
from .connection import connection_index_decorator, connection_index_processor


def get_searches(request):
    spotify_user = SpotifyUser(request.session_user)
    return starred_track_searches(spotify_user)

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
    lastfm_user = LastfmUser(request.session_user)
    if lastfm_user.connection.is_connected():
        spotify_user = SpotifyUser(request.session_user)
        if spotify_user.connection.is_connected():
            context['tracks'] = get_tracks_data(request)
    return render_to_response('index.html', context_instance=RequestContext(request, context, [connection_index_processor]))

def result_update(request):
    spotify_user = SpotifyUser(request.session_user)
    if spotify_user.connection.is_connected():
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
    