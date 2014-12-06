from unittest.mock import call

import pytest

from ..strategies import (
    separate_search_strategy,
    combined_search_strategy,
)
from .fixtures import lastfm_app


@pytest.fixture
def parser(create_patch):
    patch = create_patch('starstoloves.lib.search.strategies.LastfmResultParser')
    return patch.return_value


class TestSeparateSearchStrategy():

    def test_searches_with_track_and_artist(self, lastfm_app):
        separate_search_strategy('track_1_track', 'track_1_artist')
        assert lastfm_app.track.search.call_args_list[0] == call('track_1_track', 'track_1_artist')


    def test_returns_parsed_search_result(self, lastfm_app, parser):
        assert separate_search_strategy('track_1_track', 'track_1_artist') == parser.parse.return_value
        assert parser.parse.call_args == call(lastfm_app.track.search.return_value)


    def test_returns_none_when_search_throws(self, lastfm_app):
        lastfm_app.track.search.side_effect = TypeError
        assert separate_search_strategy('track_1_track', 'track_1_artist') == None


class TestCombinedSearchStrategy():

    def test_searches_with_track_and_artist_names_combined(self, lastfm_app):
        combined_search_strategy('track_1_track', 'track_1_artist')
        assert lastfm_app.track.search.call_args_list[0] == call('track_1_track track_1_artist')


    def test_returns_parsed_search_result(self, lastfm_app, parser):
        assert combined_search_strategy('track_1_track', 'track_1_artist') == parser.parse.return_value
        assert parser.parse.call_args == call(lastfm_app.track.search.return_value)


    def test_returns_none_when_search_throws(self, lastfm_app):
        lastfm_app.track.search.side_effect = TypeError
        assert combined_search_strategy('track_1_track', 'track_1_artist') == None