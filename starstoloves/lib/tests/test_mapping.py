from unittest.mock import MagicMock, call

import pytest

from starstoloves.lib.track.spotify_track import SpotifyTrack
from starstoloves.lib.track.lastfm_track import LastfmTrack
from starstoloves.lib.search.query import LastfmQuery
from ..mapping import TrackMapping



@pytest.fixture
def spotify_track():
    return SpotifyTrack(
        track_name='some_track',
        artist_name='some_artist',
    )


@pytest.fixture
def lastfm_tracks():
    return [
        LastfmTrack(
            url='track_1_url',
            track_name='track_1_track',
            artist_name='track_1_artist',
        ),
        LastfmTrack(
            url='track_2_url',
            track_name='track_2_track',
            artist_name='track_2_artist',
        ),
        LastfmTrack(
            url='track_3_url',
            track_name='track_3_track',
            artist_name='track_3_artist',
        )
    ]


@pytest.fixture
def loved_tracks():
    return [
        LastfmTrack(
            url='track_2_url',
        ),
        LastfmTrack(
            url='track_3_url',
        ),
    ]


@pytest.fixture
def query():
    return MagicMock(spec=LastfmQuery)


@pytest.fixture
def query_repository(create_patch, query):
    patch = create_patch('starstoloves.lib.mapping.query_repository')
    patch.get_or_create.return_value = query
    return patch



@pytest.mark.usefixtures('query_repository')
class TestTrackMapping():


    def test_track_is_given_spotify_track(self, spotify_track):
        mapping = TrackMapping(spotify_track)
        assert mapping.track is spotify_track


    def test_starts_search(self, spotify_track, query_repository, query):
        mapping = TrackMapping(spotify_track)
        assert query_repository.get_or_create.call_args == call('some_track', 'some_artist')
        assert mapping.query is query


    def test_id_is_query_id(self, spotify_track, query):
        mapping = TrackMapping(spotify_track)
        assert mapping.id is query.id


    def test_status_is_query_status(self, spotify_track, query):
        mapping = TrackMapping(spotify_track)
        assert mapping.status is query.status



@pytest.mark.usefixtures('query_repository')
class TestTrackMappingResults():


    def test_returns_query_results(self, spotify_track, query, lastfm_tracks):
        query.results = lastfm_tracks
        mapping = TrackMapping(spotify_track)
        assert mapping.results is lastfm_tracks


    def test_returns_none_when_there_are_no_results(self, spotify_track, query):
        query.results = None
        mapping = TrackMapping(spotify_track)
        assert mapping.results is None


    def test_marks_loved_status(self, spotify_track, query, lastfm_tracks, loved_tracks):
        query.results = lastfm_tracks
        mapping = TrackMapping(spotify_track, loved_tracks)
        assert self._track_by_url(mapping.results, 'track_1_url').loved == False
        assert self._track_by_url(mapping.results, 'track_2_url').loved == True
        assert self._track_by_url(mapping.results, 'track_3_url').loved == True


    def test_does_not_mutate_query_results(self, spotify_track, query, lastfm_tracks, loved_tracks):
        query.results = lastfm_tracks
        mapping = TrackMapping(spotify_track, loved_tracks)
        assert query.results[0].loved == False
        assert query.results[1].loved == False
        assert query.results[2].loved == False


    def test_moves_loved_tracks_to_the_top_of_the_list(self, spotify_track, query, lastfm_tracks, loved_tracks):
        query.results = lastfm_tracks
        mapping = TrackMapping(spotify_track, loved_tracks)
        assert mapping.results[0].url == 'track_2_url'
        assert mapping.results[1].url == 'track_3_url'
        assert mapping.results[2].url == 'track_1_url'


    def _track_by_url(self, tracks, url):
        return [track for track in tracks if track.url == url][0]
