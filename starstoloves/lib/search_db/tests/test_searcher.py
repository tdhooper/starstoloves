from unittest.mock import patch, call, MagicMock

import pytest

from celery.result import AsyncResult

from ..searcher import LastfmSearcher
from ..query import LastfmCachingQuery
from starstoloves.models import LastfmSearch


pytestmark = pytest.mark.django_db

@pytest.fixture
def task_patch(request, task_result):
    patcher = patch('starstoloves.lib.search_db.searcher.search_lastfm')
    def fin():
        patcher.stop()
    request.addfinalizer(fin)
    task_patch = patcher.start()
    task_patch.delay.return_value = task_result
    return task_patch

@pytest.fixture
def task_result():
    result = MagicMock(spec=AsyncResult).return_value
    result.id = 'some_id'
    return result

@pytest.fixture
def LastfmSearch_patch(request):
    patcher = patch('starstoloves.lib.search_db.searcher.LastfmSearch')
    def fin():
        patcher.stop()
    request.addfinalizer(fin)
    return patcher.start()

@pytest.fixture
def LastfmQuery_patch(request):
    patcher = patch('starstoloves.lib.search_db.searcher.LastfmCachingQuery')
    def fin():
        patcher.stop()
    request.addfinalizer(fin)
    return patcher.start()

@pytest.fixture
def LastfmQuery_mock(LastfmQuery_patch):
    LastfmQuery_patch.side_effect = LastfmCachingQuery
    return LastfmQuery_patch

@pytest.fixture
def searcher():
    return LastfmSearcher('some_lastfm_app')

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

def test_search_returns_a_new_query_created_with_the_task_id(task_patch, searcher, LastfmQuery_patch, LastfmSearch_patch, track):
    LastfmSearch_patch.objects.get_or_create.return_value = (MagicMock(), True)
    query = searcher.search(track)
    assert LastfmQuery_patch.call_args == call('some_id')
    assert query is LastfmQuery_patch.return_value

def test_search_stores_the_query_against_the_track(searcher, track):
    query = searcher.search(track)
    search = LastfmSearch.objects.get(track_name=track['track_name'], artist_name=track['artist_name'])
    assert search.query == query.query_model

def test_search_only_creates_one_task_when_called_twice(task_patch, searcher, track):
    searcher.search(track)
    searcher.search(track)
    assert task_patch.delay.call_count is 1

def test_search_returns_a_query_when_called_twice(task_patch, searcher, track):
    searcher.search(track)
    query = searcher.search(track)
    assert isinstance(query, LastfmCachingQuery)

def test_search_uses_the_same_task_when_called_twice(task_patch, searcher, LastfmQuery_mock, track):
    searcher.search(track)
    searcher.search(track)
    assert LastfmQuery_mock.call_args_list[0] == call('some_id')
    assert LastfmQuery_mock.call_args_list[1] == call('some_id')
