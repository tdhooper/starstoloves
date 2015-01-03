import json
import re
from operator import attrgetter

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
    disconnect_spotify as connection_disconnect_spotify,
    disconnect_lastfm as connection_disconnect_lastfm
)


# TODO: Only start a few searches at a time
def get_track_mappings(request):
    return [
        TrackMapping(track, request.session_user.loved_tracks())
        for track in sorted(
            request.session_user.starred_tracks,
            key=attrgetter('added'),
            reverse=True,
        )
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
        request.session_user.reload_starred_tracks()
    return connection_disconnect_spotify(request)


@connection_status_decorator
def disconnect_lastfm(request):
    if request.is_lastfm_connected:
        request.session_user.reload_loved_tracks()
    return connection_disconnect_lastfm(request)


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
    mappings = get_track_mappings(request)
    mappings_by_id = {mapping.id: mapping for mapping in mappings}
    for mapping_id, urls in request.POST.lists():
        mapping = mappings_by_id.get(mapping_id)
        if mapping:
            for url in urls:
                track = lastfm_track_repository.get(url)
                if track:
                    request.session_user.love_track(track, mapping.track.added.timestamp())

    request.session_user.reload_loved_tracks()

    return redirect('index')


def reload_lastfm(request):
    request.session_user.reload_loved_tracks()
    return redirect('index')


def reload_spotify(request):
    request.session_user.reload_starred_tracks()
    return redirect('index')
