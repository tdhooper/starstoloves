from unittest.mock import patch, call, Mock

import pytest

from ..query import LastfmQuery


pytestmark = pytest.mark.django_db


@pytest.fixture
def parser(create_patch):
    patch = create_patch('starstoloves.lib.search.query.LastfmResultParser')
    return patch.return_value


@pytest.fixture
def AsyncResult_patch(create_patch):
    return create_patch('starstoloves.lib.search.query.AsyncResult')


@pytest.fixture
def query(request):
    return LastfmQuery('some_id')


@pytest.fixture
def revoke_patch(create_patch):
    return create_patch('starstoloves.lib.search.query.revoke')


@pytest.fixture
def async_result_has_data(AsyncResult_patch):
    AsyncResult_patch.return_value.info = 'some_data'


@pytest.fixture
def parser_returns_tracks(request, parser):
    parser.parse.return_value = request.cls.parsed_tracks




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
