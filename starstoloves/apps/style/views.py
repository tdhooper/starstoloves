from datetime import datetime
from collections import namedtuple

from django.shortcuts import render

from starstoloves.lib.mapping import TrackMapping
from starstoloves.lib.track.spotify_track import SpotifyPlaylistTrack
from starstoloves.lib.track.lastfm_track import LastfmTrack, LastfmPlaylistTrack
from starstoloves.lib.search.query import LastfmQuery


AsyncResult = namedtuple('AsyncResult', ['status'])


def track_mapping(track, status, results=None, loved_tracks=None):
    mapping = TrackMapping(track, loved_tracks)
    async_result = AsyncResult(status)
    query = LastfmQuery(None, None, None, async_result, results)
    mapping.query = query
    return mapping


def style(request):

    loved_tracks = [
        LastfmPlaylistTrack(None, 'http://www.last.fm/music/Danger/_/11h30+(DatA+Remix)', datetime.fromtimestamp(123456)),
    ]

    mappings = [
        track_mapping(
            SpotifyPlaylistTrack(None, 'DPM', 'Vessel', datetime.fromtimestamp(123456)),
            'PENDING',
        ),
        track_mapping(
            SpotifyPlaylistTrack(None, 'Highly Explicit - Huoratron Remix', 'Mixhell', datetime.fromtimestamp(123456)),
            'STARTED',
        ),
        track_mapping(
            SpotifyPlaylistTrack(None, 'V Day Baby', 'Cristobal Tapia de Veer', datetime.fromtimestamp(123456)),
            'RETRY',
        ),
        track_mapping(
            SpotifyPlaylistTrack(None, 'CIRCLONT14 [152.97][shrymoming mix]', 'Aphex Twin', datetime.fromtimestamp(123456)),
            'FAILURE',
        ),
        track_mapping(
            SpotifyPlaylistTrack(None, 'Toothpaste', 'Igorrr', datetime.fromtimestamp(123456)),
            'REVOKED',
        ),
        track_mapping(
            SpotifyPlaylistTrack(None, '11h30 - datA remix', 'Danger', datetime.fromtimestamp(123456)),
            'SUCCESS',
            [
                LastfmTrack(
                    track_name='11h30 (DatA Remix)',
                    artist_name='Danger',
                    url='http://www.last.fm/music/Danger/_/11h30+(DatA+Remix)',
                    listeners=114502,
                ),
                LastfmTrack(
                    track_name='11h30 - DatA Remix',
                    artist_name='Danger',
                    url='http://www.last.fm/music/+noredirect/Danger/_/11h30+-+DatA+Remix',
                    listeners=12974,
                ),
                LastfmTrack(
                    track_name='11h30  (DatA Remix)',
                    artist_name='Danger',
                    url='http://www.last.fm/music/Danger/_/11h30++(DatA+Remix)',
                    listeners=1939,
                ),
            ],
            loved_tracks
        ),
    ]

    return render(request, 'style.html', {
        'mappings': mappings
    })
