from unittest.mock import patch, call

import pytest

from ..query import LastfmQuery
from .fixtures import *


@pytest.fixture
def AsyncResult_patch(request):
    return create_patch(request, 'starstoloves.lib.search_db.query.AsyncResult')

@pytest.fixture
def query(parser):
    return LastfmQuery('some_id', parser)

@pytest.fixture
def revoke_patch(request):
    return create_patch(request, 'starstoloves.lib.search_db.query.revoke')


def test_fetches_async_result_on_init(AsyncResult_patch, query):
    assert AsyncResult_patch.call_args == call('some_id')

def test_status_is_async_result_status(AsyncResult_patch, query):
    AsyncResult_patch.return_value.status = 'SOME_STATUS'
    assert query.status == 'SOME_STATUS'

def test_results_is_none_when_not_ready(AsyncResult_patch, query):
    AsyncResult_patch.return_value.ready.return_value = False
    assert query.results is None

def test_results_parses_async_result_info(AsyncResult_patch, parser, query):
    AsyncResult_patch.return_value.info = 'some_data'
    parser.parse.return_value = 'parsed_data'
    assert query.results == 'parsed_data'
    assert parser.parse.call_args == call('some_data')

def test_stop_revokes_task(revoke_patch, query):
    query.stop()
    assert revoke_patch.call_args == call('some_id')
