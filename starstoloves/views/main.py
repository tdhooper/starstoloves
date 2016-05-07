import json
import re
from operator import attrgetter
from itertools import chain

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
    connect_lastfm as connection_connect_lastfm,
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
    if request.is_lastfm_connected() and request.is_spotify_connected():
        try:
            context['mappings'] = get_track_mappings(request)
        except Exception as e:
            context['error'] = e
    return render_to_response('index.html', context_instance=RequestContext(request, context, [connection_index_processor]))


@connection_status_decorator
def connect_lastfm(request):
    response = connection_connect_lastfm(request)
    if request.is_lastfm_connected():
        request.session_user.loved_tracks()
    return response


@connection_status_decorator
def disconnect_spotify(request):
    if request.is_spotify_connected():
        for mapping in get_track_mappings(request):
            mapping.query.stop()
        request.session_user.reload_starred_tracks()
    return connection_disconnect_spotify(request)


@connection_status_decorator
def disconnect_lastfm(request):
    if request.is_lastfm_connected():
        request.session_user.reload_loved_tracks()
    return connection_disconnect_lastfm(request)


@connection_status_decorator
def result_update(request):
    if request.is_spotify_connected():
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
    mappings_by_id = {
        mapping.id: mapping
        for mapping in get_track_mappings(request)
    }

    tracks_to_love = list(chain.from_iterable([
        [
            {
                'track': track,
                'timestamp': mapping.track.added.timestamp(),
            }
            for track in [
                lastfm_track_repository.get(url)
                for url in urls
            ] if track
        ]
        for mapping, urls in [
            (mappings_by_id.get(mapping_id), urls)
            for mapping_id, urls in request.POST.lists()
        ] if mapping
    ]))

    if tracks_to_love:
        request.session_user.love_tracks(tracks_to_love)

    request.session_user.reload_loved_tracks()

    return redirect('index')


def reload_lastfm(request):
    request.session_user.reload_loved_tracks()
    return redirect('index')


def reload_spotify(request):
    request.session_user.reload_starred_tracks()
    return redirect('index')
