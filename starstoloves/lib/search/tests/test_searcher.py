from unittest.mock import patch, call

import pytest

from starstoloves.lib.track.spotify_track import SpotifyTrack
from ..searcher import LastfmSearcher


@pytest.fixture
def searcher():
    return LastfmSearcher()


@pytest.fixture
def track():
    return SpotifyTrack('some_track', 'some_artist')


@pytest.fixture
def query_repository(create_patch):
    return create_patch('starstoloves.lib.search.searcher.query_repository')


def test_search_proxies_to_query_repository(searcher, track, query_repository):
    query = searcher.search(track)
    assert query_repository.get_or_create.call_args == call('some_track', 'some_artist')
    assert query == query_repository.get_or_create.return_value
