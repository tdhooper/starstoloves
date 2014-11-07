from unittest.mock import call

import pytest

from starstoloves.lib.track import lastfm_track_repository
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
def parser(create_patch):
    patch = create_patch('starstoloves.lib.search.query.LastfmResultParser')
    return patch.return_value




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


    @pytest.mark.with_results
    def test_returns_results_when_provided(self, query):
        assert query.results is 'some_results'


    @pytest.mark.with_async_result
    def test_none_when_async_result_is_not_ready(self, query, async_result):
        async_result.ready.return_value = False
        assert query.results is None


    @pytest.mark.with_async_result
    def test_does_not_parse_when_async_result_is_not_ready(self, query, async_result, parser):
        async_result.ready.return_value = False
        assert query.results is None
        assert parser.parse.call_count is 0


    @pytest.mark.with_async_result
    def test_returns_parsed_async_result_info_when_ready(self, query, async_result, parser):
        async_result.info = 'some_data'
        parser.parse.return_value = 'some_results'
        assert query.results == 'some_results'
        assert parser.parse.call_count is 1
        assert parser.parse.call_args == call('some_data')


    @pytest.mark.with_async_result
    def test_saves_results_when_parsed(self, query, async_result, parser, query_repository):
        async_result.info = 'some_data'
        parser.parse.return_value = 'some_results'
        query.results
        assert query_repository.save.call_args == call(query)


    @pytest.mark.with_async_result
    def test_does_not_save_results_when_there_are_none(self, query, async_result, parser, query_repository):
        async_result.info = 'some_data'
        parser.parse.return_value = None
        query.results
        assert query_repository.save.call_count is 0


    @pytest.mark.with_async_result
    def test_memoises_parsed_async_result_info(self, query, async_result, parser):
        async_result.info = 'some_data'
        parser.parse.return_value = 'some_results'
        assert query.results == 'some_results'
        assert query.results == 'some_results'
        assert parser.parse.call_count is 1




@pytest.mark.with_async_result
def test_stop_revokes_task(query, revoke):
    query.stop()
    assert revoke.call_args == call('some_id')
