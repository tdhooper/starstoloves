import json
import re

from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError

from starstoloves.lib.track import lastfm_track_repository
from starstoloves.lib.mapping import TrackMapping
from .connection import (
    connection_index_decorator,
    connection_index_processor,
    connection_status_decorator,
    disconnect_spotify as connection_disconnect_spotify
)



def get_track_mappings(request):
    return [
        TrackMapping(track)
        for track in request.session_user.starred_tracks
    ]


@connection_index_decorator
@connection_status_decorator
def index(request):
    context = {}
    if request.is_lastfm_connected and request.is_spotify_connected:
        context['mappings'] = get_track_mappings(request)
    return render_to_response('index.html', context_instance=RequestContext(request, context, [connection_index_processor]))


@connection_status_decorator
def disconnect_spotify(request):
    if request.is_spotify_connected:
        for mapping in get_track_mappings(request):
            mapping.query.stop()
    return connection_disconnect_spotify(request)


@connection_status_decorator
def result_update(request):
    if request.is_spotify_connected:
        mappings = get_track_mappings(request)
        status_by_id = {
            re.search('status\[(.+)\]', key).groups()[0]: value
            for key, value in request.POST.items()
        }
        if status_by_id:
            mappings = [
                mapping
                for mapping in mappings
                if
                    not mapping.id in status_by_id
                    or mapping.status != status_by_id[mapping.id]
            ]
        results = [
            {
                'id': mapping.id,
                'status': mapping.status,
                'html': render(request, 'result.html', {'mapping': mapping}).content.decode("utf-8"),
            }
            for mapping in mappings
        ]
        return HttpResponse(json.dumps(results), content_type="application/json")
    return HttpResponse('No results', status=401)


def love_tracks(request):
    tracks = list(filter(None, [
        lastfm_track_repository.get(url)
        for url in request.POST.getlist('love_tracks')
    ]))
    request.session_user.love_tracks(tracks)
    return redirect('index')
