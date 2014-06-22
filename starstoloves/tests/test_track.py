import unittest
from unittest.mock import MagicMock

from starstoloves.lib.search import LastfmSearch, LastfmSearchQuery
from starstoloves.lib.track import SearchingTrackFactory

class TestSearchingTrack(unittest.TestCase):

    def setUp(self):
        MockLastfmSearch = MagicMock(spec=LastfmSearch)
        self.search = MockLastfmSearch('some_lastfm_app')

        self.MockLastfmSearchQuery = MagicMock(spec=LastfmSearchQuery)
        self.search_query = self.MockLastfmSearchQuery('some_id')
        self.search_query.data = {'id': 'some_id', 'status': 'PENDING', 'tracks': None}

        self.search.search.return_value = self.search_query
        self.search.deserialise.return_value = self.search_query
        self.factory = SearchingTrackFactory(self.search)
        self.track = self.factory.create('some_track_name', 'some_artist_name', 1275493486)

    def test_search_creates_a_new_search(self):
        self.track.search
        self.search.search.assert_called_with('some_track_name some_artist_name')

    def test_search_returns_the_search_query(self):
        self.assertIs(self.track.search, self.search_query)

    def test_search_doesnt_create_a_new_search_when_called_twice(self):
        self.track.search
        self.track.search
        self.assertEqual(self.search.search.call_count, 1)

    def test_search_doesnt_create_a_new_search_when_given_a_serialised_query(self):
        serialised_track = {
            'track_name': 'some_track_name',
            'artist_name': 'some_artist_name',
            'date_saved': 1275493486,
            'serialised_query': {
                'id': 'some_id',
                'status': 'PENDING',
                'result': None
            }
        }
        track = self.factory.deserialise(serialised_track)
        track.search
        self.assertFalse(self.search.search.called)

    def test_search_deserialises_the_query_when_given_a_serialised_query(self):
        serialised_track = {
            'track_name': 'some_track_name',
            'artist_name': 'some_artist_name',
            'date_saved': 1275493486,
            'serialised_query': {
                'id': 'some_other_id',
                'status': 'SUCCESS',
                'result': 'some_result'
            }
        }
        deserialised_query = self.MockLastfmSearchQuery('some_other_id')
        self.search.deserialise.return_value = deserialised_query
        track = self.factory.deserialise(serialised_track)
        self.assertEqual(track.search, deserialised_query)

    def test_can_be_serialised_and_deserialised(self):
        serialised_track = self.track.serialise()
        track = self.factory.deserialise(serialised_track)
        self.assertEqual(track.track_name, self.track.track_name)
        self.assertEqual(track.artist_name, self.track.artist_name)
        self.assertEqual(track.date_saved, self.track.date_saved)
        self.assertEqual(track.search, self.track.search)

