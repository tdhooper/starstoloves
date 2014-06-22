import unittest
from unittest.mock import MagicMock

from starstoloves.lib.search import LastfmSearch, LastfmSearchQuery
from starstoloves.lib.track import SearchingTrack

class TestSearchingTrack(unittest.TestCase):

    def setUp(self):
        MockLastfmSearch = MagicMock(spec=LastfmSearch)
        self.search = MockLastfmSearch('some_lastfm_app')

        MockLastfmSearchQuery = MagicMock(spec=LastfmSearchQuery)
        self.search_query = MockLastfmSearchQuery('some_id')
        self.search_query.data = {'id': 'some_id', 'status': 'PENDING'}

        def search_side_effect(track_name, artist_name):
            return self.search_query

        def query_side_effect(id):
            return self.search_query

        self.search.search = MagicMock(side_effect=search_side_effect)
        self.search.query = MagicMock(side_effect=query_side_effect)
        self.track = SearchingTrack('some_track_name', 'some_artist_name', 1275493486, self.search)

    def test_search_creates_a_new_search(self):
        self.track.search
        self.search.search.assert_called_with('some_track_name', 'some_artist_name')

    def test_search_doesnt_retrieve_the_new_search_query(self):
        self.track.search
        self.assertFalse(self.search.query.called)

    def test_search_returns_the_search_query_data(self):
        self.assertIs(self.track.search, self.search_query.data)

    def test_search_doesnt_create_a_new_search_when_called_twice(self):
        self.track.search
        self.track.search
        self.assertEqual(self.search.search.call_count, 1)

    def test_search_doesnt_create_a_new_search_when_given_query_data(self):
        query_data = {'id': 'some_id', 'status': 'PENDING'}
        track = SearchingTrack('some_track_name', 'some_artist_name', 1275493486, self.search, query_data)
        track.search
        self.assertFalse(self.search.search.called)

    def test_search_retrieves_the_search_query_when_called_twice(self):
        self.track.search
        self.track.search
        self.search.query.assert_called_with('some_id')

    def test_search_retrieves_the_search_query_when_given_query_data(self):
        query_data = {'id': 'some_other_id', 'status': 'PENDING'}
        track = SearchingTrack('some_track_name', 'some_artist_name', 1275493486, self.search, query_data)
        track.search
        self.search.query.assert_called_with('some_other_id')

    def test_search_just_returns_the_query_data_if_given_query_status_is_success(self):
        query_data = {'status': 'SUCCESS'}
        track = SearchingTrack('some_track_name', 'some_artist_name', 1275493486, self.search, query_data)
        self.assertIs(track.search, query_data)
        self.assertFalse(self.search.query.called)

    def test_search_just_returns_the_query_data_if_given_query_status_is_failure(self):
        query_data = {'status': 'FAILURE'}
        track = SearchingTrack('some_track_name', 'some_artist_name', 1275493486, self.search, query_data)
        self.assertIs(track.search, query_data)
        self.assertFalse(self.search.query.called)

    def test_search_just_returns_the_query_data_when_status_is_success(self):
        self.track.search
        self.search_query.data = {'status': 'SUCCESS'}
        self.track.search
        self.assertIs(self.track.search, self.search_query.data)
        self.assertEqual(self.search.search.call_count, 1)
        self.assertEqual(self.search.query.call_count, 1)

    def test_search_just_returns_the_query_data_when_status_is_failure(self):
        self.track.search
        self.search_query.data = {'status': 'FAILURE'}
        self.track.search
        self.assertIs(self.track.search, self.search_query.data)
        self.assertEqual(self.search.search.call_count, 1)
        self.assertEqual(self.search.query.call_count, 1)
