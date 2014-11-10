from unittest.mock import call

import pytest

from ..task import search_lastfm




@pytest.fixture
def lastfm_app(create_patch):
    return create_patch('starstoloves.lib.search.task.lastfm_app')


@pytest.fixture
def parser(create_patch):
    patch = create_patch('starstoloves.lib.search.task.LastfmResultParser')
    return patch.return_value



def test_searches_with_track_and_artist(lastfm_app):
    search_lastfm('some_track', 'some_artist')
    assert lastfm_app.track.search.call_args == call('some_track', 'some_artist')


def test_returns_parsed_search_result(lastfm_app, parser):
    assert search_lastfm('some_track', 'some_artist') == parser.parse.return_value
    assert parser.parse.call_args == call(lastfm_app.track.search.return_value)


def test_catches_exceptions(lastfm_app):
    lastfm_app.track.search.side_effect = TypeError
    assert search_lastfm('some_track', 'some_artist') == None