from unittest.mock import patch, call, MagicMock

import pytest

from celery.result import AsyncResult

from ..searcher import LastfmSearcher
from .fixtures import *


@pytest.fixture
def task_patch(request):
    patcher = patch('starstoloves.lib.search_db.searcher.search_lastfm')
    def fin():
        patcher.stop()
    request.addfinalizer(fin)
    return patcher.start()

@pytest.fixture
def task_result(task_patch):
    result = MagicMock(spec=AsyncResult).return_value
    task_patch.delay.return_value = result
    return result

@pytest.fixture
def LastfmQuery_patch(request):
    patcher = patch('starstoloves.lib.search_db.searcher.LastfmQuery')
    def fin():
        patcher.stop()
    request.addfinalizer(fin)
    return patcher.start()

@pytest.fixture
def searcher(parser):
    return LastfmSearcher('some_lastfm_app', parser)

@pytest.fixture
def track():
    return {
        'track_name': 'some_track',
        'artist_name': 'some_artist',
    }

def test_search_creates_a_new_task(task_patch, searcher, track):
    searcher.search(track)
    assert task_patch.delay.call_count is 1
    assert task_patch.delay.call_args == call('some_lastfm_app', 'some_track', 'some_artist')

def test_search_returns_a_new_query_created_with_the_task_id(task_result, searcher, parser, LastfmQuery_patch, track):
    task_result.id = 'some_id'
    query = searcher.search(track)
    assert LastfmQuery_patch.call_args == call('some_id', parser)
    assert query is LastfmQuery_patch.return_value
