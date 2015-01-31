from datetime import datetime, timezone
from unittest.mock import MagicMock, call

import pytest

from starstoloves.lib.track.spotify_track import SpotifyPlaylistTrack
from starstoloves.lib.track.lastfm_track import LastfmTrack, LastfmPlaylistTrack
from starstoloves.lib.search.query import LastfmQuery
from ..mapping import TrackMapping



@pytest.fixture
def spotify_track():
    return SpotifyPlaylistTrack(
        track_name='some_track',
        artist_name='some_artist',
        user=None,
        added=datetime(1970, 1, 1, 0, 0, 12, tzinfo=timezone.utc),
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
        LastfmPlaylistTrack(
            user=None,
            url='track_2_url',
            added=datetime(1970, 1, 1, 0, 0, 12),
        ),
        LastfmPlaylistTrack(
            user=None,
            url='track_3_url',
            added=datetime(1970, 1, 1, 0, 0, 34),
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


    def test_returns_query_results_as_track_in_dicts(self, spotify_track, query, lastfm_tracks):
        query.results = lastfm_tracks
        mapping = TrackMapping(spotify_track)
        assert len(mapping.results) is 3
        assert mapping.results[0]['track'] is lastfm_tracks[0]
        assert mapping.results[1]['track'] is lastfm_tracks[1]
        assert mapping.results[2]['track'] is lastfm_tracks[2]


    def test_returns_none_when_there_are_no_results(self, spotify_track, query):
        query.results = None
        mapping = TrackMapping(spotify_track)
        assert mapping.results is None


    def test_marks_loved_status_as_false_by_default(self, spotify_track, query, lastfm_tracks):
        query.results = lastfm_tracks
        mapping = TrackMapping(spotify_track)
        assert self._result_by_url(mapping.results, 'track_1_url')['loved'] == False
        assert self._result_by_url(mapping.results, 'track_2_url')['loved'] == False
        assert self._result_by_url(mapping.results, 'track_3_url')['loved'] == False


    def test_marks_loved_status_as_time(self, spotify_track, query, lastfm_tracks, loved_tracks):
        query.results = lastfm_tracks
        mapping = TrackMapping(spotify_track, loved_tracks)
        assert self._result_by_url(mapping.results, 'track_1_url')['loved'] == False
        assert self._result_by_url(mapping.results, 'track_2_url')['loved'] == datetime(1970, 1, 1, 0, 0, 12)
        assert self._result_by_url(mapping.results, 'track_3_url')['loved'] == datetime(1970, 1, 1, 0, 0, 34)


    def test_moves_loved_tracks_to_the_top_of_the_list(self, spotify_track, query, lastfm_tracks, loved_tracks):
        query.results = lastfm_tracks
        mapping = TrackMapping(spotify_track, loved_tracks)
        assert mapping.results[0]['track'].url == 'track_2_url'
        assert mapping.results[1]['track'].url == 'track_3_url'
        assert mapping.results[2]['track'].url == 'track_1_url'


    def test_marks_top_result_for_loving_if_unloved(
        self,
        spotify_track,
        query,
        lastfm_tracks,
    ):
        query.results = lastfm_tracks
        mapping = TrackMapping(spotify_track)
        assert mapping.results[0]['love'] == True
        assert mapping.results[1]['love'] == False
        assert mapping.results[2]['love'] == False


    def test_doesnt_mark_top_result_for_loving_if_loved_before_added(
        self,
        spotify_track,
        query,
        lastfm_tracks,
        loved_tracks,
    ):
        query.results = lastfm_tracks
        mapping = TrackMapping(spotify_track, loved_tracks)
        assert mapping.results[0]['love'] == False
        assert mapping.results[1]['love'] == False
        assert mapping.results[2]['love'] == False


    def test_marks_top_result_for_loving_if_loved_after_added(
        self,
        spotify_track,
        query,
        lastfm_tracks,
        loved_tracks,
    ):
        query.results = lastfm_tracks
        spotify_track.added = datetime.fromtimestamp(1)
        mapping = TrackMapping(spotify_track, loved_tracks)
        assert mapping.results[0]['love'] == True
        assert mapping.results[1]['love'] == False
        assert mapping.results[2]['love'] == False


    def _result_by_url(self, results, url):
        return [result for result in results if result['track'].url == url][0]
