import unittest
from unittest.mock import MagicMock

from starstoloves.lib.search import LastfmSearch, LastfmSearchQuery
from starstoloves.lib.track import SearchingTrack

class TestSearchingTrack(unittest.TestCase):

    def setUp(self):
        MockLastfmSearch = MagicMock(spec=LastfmSearch)
        self.search = MockLastfmSearch('some_lastfm_app')

        self.MockLastfmSearchQuery = MagicMock(spec=LastfmSearchQuery)
        self.search_query = self.MockLastfmSearchQuery('some_id')
        self.search_query.data = {'id': 'some_id', 'status': 'PENDING', 'tracks': None}

        self.search.search.return_value = self.search_query
        self.search.deserialise.return_value = self.search_query
        self.track = SearchingTrack('some_track_name', 'some_artist_name', 1275493486, self.search)

    def test_search_creates_a_new_search(self):
        self.track.search
        self.search.search.assert_called_with('some_track_name', 'some_artist_name')

    def test_search_returns_the_search_query(self):
        self.assertIs(self.track.search, self.search_query)

    def test_search_doesnt_create_a_new_search_when_called_twice(self):
        self.track.search
        self.track.search
        self.assertEqual(self.search.search.call_count, 1)

    def test_search_doesnt_create_a_new_search_when_given_a_serialised_query(self):
        query = {'id': 'some_id', 'status': 'PENDING', 'result': None}
        track = SearchingTrack('some_track_name', 'some_artist_name', 1275493486, self.search, query)
        track.search
        self.assertFalse(self.search.search.called)

    def test_search_deserialises_the_query_when_given_a_serialised_query(self):
        query = {'id': 'some_other_id', 'status': 'SUCCESS', 'result': 'some_result'}
        deserialised_query = self.MockLastfmSearchQuery('some_id')
        self.search.deserialise.return_value = deserialised_query
        track = SearchingTrack('some_track_name', 'some_artist_name', 1275493486, self.search, query)
        self.assertEqual(track.search, deserialised_query)
