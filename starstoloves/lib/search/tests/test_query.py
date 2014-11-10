from unittest.mock import call

import pytest

from starstoloves.lib.track import lastfm_track_repository
from starstoloves.lib.track.lastfm_track import LastfmTrack
from ..query import LastfmQuery
from .fixtures import *


pytestmark = pytest.mark.django_db


@pytest.fixture
def revoke(create_patch):
    return create_patch('starstoloves.lib.search.query.revoke')


@pytest.fixture
def query_repository(create_patch):
    return create_patch('starstoloves.lib.search.query_repository')


@pytest.fixture
def query(request, query_repository, async_result):
    if 'with_async_result' in request.keywords:
        return LastfmQuery(query_repository, 'some_track', 'some_artist', async_result)
    elif 'with_results' in request.keywords:
        return LastfmQuery(query_repository, 'some_track', 'some_artist', None, 'some_results')
    else:
        return LastfmQuery(query_repository, 'some_track', 'some_artist')


@pytest.fixture
def search_lastfm(create_patch, async_result):
    return create_patch('starstoloves.lib.search.query.search_lastfm')


@pytest.fixture
def lastfm_track_repository(create_patch):
    return create_patch('starstoloves.lib.search.query.lastfm_track_repository')




class TestAsyncResult():


    @pytest.mark.with_async_result
    def test_returns_async_result_when_provided(self, query, async_result):
        assert query.async_result is async_result


    @pytest.mark.with_async_result
    def test_does_not_save_async_result_when_provided(self, query, async_result, query_repository):
        query.async_result
        assert query_repository.save.call_count is 0


    def test_starts_search_task(self, query, search_lastfm):
        assert query.async_result is search_lastfm.delay.return_value
        assert search_lastfm.delay.call_count is 1
        assert search_lastfm.delay.call_args == call('some_track', 'some_artist')


    def test_memoises_created_async_result(self, query, search_lastfm):
        assert query.async_result is search_lastfm.delay.return_value
        assert query.async_result is search_lastfm.delay.return_value
        assert search_lastfm.delay.call_count is 1


    def test_saves_created_async_result(self, query, search_lastfm, query_repository):
        query.async_result
        assert query_repository.save.call_args == call(query)



@pytest.mark.with_async_result
def test_status_is_async_result_status(query, async_result):
    async_result.status = 'SOME_STATUS'
    assert query.status == 'SOME_STATUS'



# TODO: Create our own id so that the task can be destroyed without loosing track of results
@pytest.mark.with_async_result
def test_id_is_async_result_id(query, async_result):
    async_result.id = 'some_id'
    assert query.id == 'some_id'



class TestResults():


    tracks = [
        LastfmTrack(
            url='some_url',
            track_name='some_track',
            artist_name='some_artist',
        ),
        LastfmTrack(
            url='another_url',
            track_name='another_track',
            artist_name='another_artist',
        )
    ]


    @pytest.mark.with_results
    def test_returns_results_when_provided(self, query):
        assert query.results is 'some_results'


    @pytest.mark.with_async_result
    def test_none_when_async_result_is_not_ready(self, query, async_result):
        async_result.ready.return_value = False
        assert query.results is None


    @pytest.mark.with_async_result
    def test_saves_and_returns_lastfm_tracks_from_async_result_info_when_ready(self, query, async_result, lastfm_track_repository):
        async_result.info = self.tracks
        results = query.results
        assert results == self.tracks
        assert lastfm_track_repository.save.call_args_list == [
            call(self.tracks[0]),
            call(self.tracks[1]),
        ]


    @pytest.mark.with_async_result
    def test_memoises_lastfm_tracks(self, query, async_result, lastfm_track_repository):
        async_result.info = self.tracks
        results = query.results
        assert query.results == results
        assert lastfm_track_repository.save.call_count == 2


    @pytest.mark.with_async_result
    def test_saves_results_when_parsed(self, query, async_result, query_repository):
        async_result.info = self.tracks
        query.results
        assert query_repository.save.call_args == call(query)


    @pytest.mark.with_async_result
    def test_does_not_save_results_when_there_are_none(self, query, async_result, query_repository):
        async_result.info = None
        query.results
        assert query_repository.save.call_count is 0




@pytest.mark.with_async_result
def test_stop_revokes_task(query, revoke):
    query.stop()
    assert revoke.call_args == call('some_id')
