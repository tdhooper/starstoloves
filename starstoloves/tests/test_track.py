import unittest
from unittest.mock import MagicMock

from starstoloves.lib.search import LastfmSearch, LastfmSearchResult
from starstoloves.lib.track import SearchingTrack

from celery.result import AsyncResult

class TestSearchingTrack(unittest.TestCase):

    def setUp(self):
        MockLastfmSearch = MagicMock(spec=LastfmSearch)
        self.search = MockLastfmSearch('some_lastfm_app')

        MockLastfmSearchResult = MagicMock(spec=LastfmSearchResult)
        self.search_result = MockLastfmSearchResult('some_id')
        self.search_result.data = {'id': 'some_id', 'status': 'PENDING'}

        def search_side_effect(track_name, artist_name):
            return self.search_result

        def result_side_effect(id):
            return self.search_result

        self.search.search = MagicMock(side_effect=search_side_effect)
        self.search.result = MagicMock(side_effect=result_side_effect)
        self.track = SearchingTrack('some_track_name', 'some_artist_name', 1275493486, self.search)

    def test_search_creates_a_new_search(self):
        self.track.search
        self.search.search.assert_called_with('some_track_name', 'some_artist_name')

    def test_search_doesnt_retrieve_the_new_search_result(self):
        self.track.search
        self.assertFalse(self.search.result.called)

    def test_search_returns_the_search_result_data(self):
        self.assertIs(self.track.search, self.search_result.data)

    def test_search_doesnt_create_a_new_search_when_called_twice(self):
        self.track.search
        self.track.search
        self.assertEqual(self.search.search.call_count, 1)

    def test_search_doesnt_create_a_new_search_when_given_result_data(self):
        result_data = {'id': 'some_id', 'status': 'PENDING'}
        track = SearchingTrack('some_track_name', 'some_artist_name', 1275493486, self.search, result_data)
        track.search
        self.assertFalse(self.search.search.called)

    def test_search_retrieves_the_search_result_when_called_twice(self):
        self.track.search
        self.track.search
        self.search.result.assert_called_with('some_id')

    def test_search_retrieves_the_search_result_when_given_result_data(self):
        result_data = {'id': 'some_other_id', 'status': 'PENDING'}
        track = SearchingTrack('some_track_name', 'some_artist_name', 1275493486, self.search, result_data)
        track.search
        self.search.result.assert_called_with('some_other_id')

    def test_search_just_returns_the_result_data_if_given_result_status_is_success(self):
        result_data = {'status': 'SUCCESS'}
        track = SearchingTrack('some_track_name', 'some_artist_name', 1275493486, self.search, result_data)
        self.assertIs(track.search, result_data)
        self.assertFalse(self.search.result.called)

    def test_search_just_returns_the_result_data_if_given_result_status_is_failure(self):
        result_data = {'status': 'FAILURE'}
        track = SearchingTrack('some_track_name', 'some_artist_name', 1275493486, self.search, result_data)
        self.assertIs(track.search, result_data)
        self.assertFalse(self.search.result.called)

    def test_search_just_returns_the_result_data_when_status_is_success(self):
        self.track.search
        self.search_result.data = {'status': 'SUCCESS'}
        self.track.search
        self.assertIs(self.track.search, self.search_result.data)
        self.assertEqual(self.search.search.call_count, 1)
        self.assertEqual(self.search.result.call_count, 1)

    def test_search_just_returns_the_result_data_when_status_is_failure(self):
        self.track.search
        self.search_result.data = {'status': 'FAILURE'}
        self.track.search
        self.assertIs(self.track.search, self.search_result.data)
        self.assertEqual(self.search.search.call_count, 1)
        self.assertEqual(self.search.result.call_count, 1)
