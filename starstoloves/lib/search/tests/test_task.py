from unittest.mock import call

import pytest

from ..task import search_lastfm




@pytest.fixture
def lastfm_app(create_patch):
    return create_patch('starstoloves.lib.search.task.lastfm_app')




def test_searches_with_track_and_artist(lastfm_app):
    search_lastfm('some_track', 'some_artist')
    assert lastfm_app.track.search.call_args == call('some_track', 'some_artist')


def test_returns_search_result(lastfm_app):
    assert search_lastfm('some_track', 'some_artist') == lastfm_app.track.search.return_value
