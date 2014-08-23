from unittest.mock import patch, call, Mock

import pytest

from starstoloves.models import LastfmQuery as LastfmQueryModel
from ..query import LastfmQuery, LastfmCachingQuery
from .fixtures import *


pytestmark = pytest.mark.django_db

@pytest.fixture
def parser(request):
    patch = create_patch(request, 'starstoloves.lib.search_db.query.LastfmResultParser')
    return patch.return_value

@pytest.fixture
def AsyncResult_patch(request):
    return create_patch(request, 'starstoloves.lib.search_db.query.AsyncResult')

@pytest.fixture(params=[LastfmQuery, LastfmCachingQuery])
def query(request, LastfmQueryModel_patch, query_model_mocks):
    if 'caching_only' in request.keywords and request.param is not LastfmCachingQuery:
        pytest.skip("LastfmCachingQuery only")

    return request.param('some_id')

@pytest.fixture
def revoke_patch(request):
    return create_patch(request, 'starstoloves.lib.search_db.query.revoke')

@pytest.fixture
def async_result_has_data(AsyncResult_patch):
    AsyncResult_patch.return_value.info = 'some_data'

@pytest.fixture
def parser_returns_tracks(request, parser):
    parser.parse.return_value = request.cls.parsed_tracks

@pytest.fixture
def LastfmQueryModel_patch(request):
    return create_patch(request, 'starstoloves.lib.search_db.query.LastfmQueryModel')

@pytest.fixture
def query_model_mocks(LastfmQueryModel_patch):
    model_mocks = []
    def get_or_create(**kwargs):
        model, created = LastfmQueryModel.objects.get_or_create(**kwargs)
        model_mock = Mock(wraps=model)
        model_mocks.append(model_mock)
        return (model_mock, created)
    LastfmQueryModel_patch.objects.get_or_create.side_effect = get_or_create
    return model_mocks

def test_fetches_async_result_on_init(AsyncResult_patch, query):
    assert AsyncResult_patch.call_args == call('some_id')

def test_status_is_async_result_status(AsyncResult_patch, query):
    AsyncResult_patch.return_value.status = 'SOME_STATUS'
    assert query.status == 'SOME_STATUS'

def test_results_is_none_when_not_ready(AsyncResult_patch, query):
    AsyncResult_patch.return_value.ready.return_value = False
    assert query.results is None

@pytest.mark.usefixtures("async_result_has_data")
def test_results_returns_parsed_AsynchResult_info(parser, query):
    parser.parse.return_value = 'parsed_tracks'
    assert query.results == 'parsed_tracks'
    assert parser.parse.call_args == call('some_data')

def test_stop_revokes_task(revoke_patch, query):
    query.stop()
    assert revoke_patch.call_args == call('some_id')

@pytest.mark.caching_only
class TestDBCachingQuery():

    parsed_tracks = [{
        'track_name': 'some_track_name',
        'artist_name': 'some_artist_name',
        'url': 'some_url',
    },{
        'track_name': 'another_track_name',
        'artist_name': 'another_artist_name',
        'url': 'another_url',
    }]

    def test_gets_or_creates_a_query_model_on_init(self, query, LastfmQueryModel_patch):
        assert LastfmQueryModel.objects.get(task_id='some_id')
        assert LastfmQueryModel_patch.objects.get_or_create.call_args == call(task_id='some_id')

    @pytest.mark.usefixtures("async_result_has_data")
    @pytest.mark.usefixtures("parser_returns_tracks")
    def test_results_stores_parsed_tracks_on_the_query_model(self, query):
        assert query.results == self.parsed_tracks

        query_model = LastfmQueryModel.objects.get(task_id='some_id')
        track_models = query_model.track_results.all()

        assert track_models[0].track_name == 'some_track_name'
        assert track_models[0].artist_name == 'some_artist_name'
        assert track_models[0].url == 'some_url'

        assert track_models[1].track_name == 'another_track_name'
        assert track_models[1].artist_name == 'another_artist_name'
        assert track_models[1].url == 'another_url'

    @pytest.mark.usefixtures("async_result_has_data")
    @pytest.mark.usefixtures("parser_returns_tracks")
    def test_results_does_not_write_twice_when_called_twice(self, query, query_model_mocks):
        assert query.results == self.parsed_tracks
        assert query.results[0] == self.parsed_tracks[0]
        assert query.results[1] == self.parsed_tracks[1]
        assert query_model_mocks[-1].track_results.add.call_count is 1
