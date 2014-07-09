import unittest
from unittest.mock import MagicMock, patch

from uuid import uuid4
from copy import copy

from starstoloves.lib.search import LastfmSearcher, LastfmSearchQuery
from starstoloves.lib.track import SearchingTrackFactory

class TestSearchingTrack(unittest.TestCase):

    def setUp(self):
        self.uuids = [uuid4(), uuid4()]
        self.uuids_clone = copy(self.uuids)
        self.patcher = patch('starstoloves.lib.track.uuid4')
        self.uuid4 = self.patcher.start()
        self.uuid4.side_effect = lambda: self.uuids_clone.pop(0);

        MockLastfmSearcher = MagicMock(spec=LastfmSearcher)
        self.searcher = MockLastfmSearcher('some_lastfm_app')

        self.MockLastfmSearchQuery = MagicMock(spec=LastfmSearchQuery)
        self.search_query = self.MockLastfmSearchQuery('some_id')
        self.search_query.status = 'SOME_STATUS'

        self.searcher.search.return_value = self.search_query
        self.searcher.deserialise.return_value = self.search_query
        self.factory = SearchingTrackFactory(self.searcher)
        self.track = self.factory.create('some_track_name', 'some_artist_name', 1275493486)

    def tearDown(self):
        self.patcher.stop()

    def test_has_a_unique_id(self):
        self.assertEqual(self.track.id, self.uuids[0].hex)

    def test_status_is_combined_query_status(self):
        self.assertEqual(self.track.status, 'SOME_STATUS')

    def test_search_creates_a_new_combined_search(self):
        self.track.search
        self.searcher.search.assert_called_with('some_track_name some_artist_name')

    def test_search_returns_the_combined_search_query(self):
        self.assertIs(self.track.search['combined'], self.search_query)

    def test_search_doesnt_create_a_new_search_when_called_twice(self):
        self.track.search
        self.track.search
        self.assertEqual(self.searcher.search.call_count, 1)

    def test_results_returns_the_combined_search_result(self):
        self.assertEqual(self.track.results, self.search_query.result)

    def test_stop_stops_the_combined_search_query(self):
        self.track.stop()
        self.assertEqual(self.search_query.stop.call_count, 1)

    def test_search_doesnt_create_a_new_search_when_given_a_serialised_query(self):
        serialised_track = {
            'track_name': 'some_track_name',
            'artist_name': 'some_artist_name',
            'date_saved': 1275493486,
            'id': 'track_id',
            'status': 'PENDING',
            'serialised_queries': {
                'combined': {
                    'id': 'some_id',
                    'status': 'PENDING',
                    'result': None,
                },
            }
        }
        track = self.factory.deserialise(serialised_track)
        track.search
        self.assertFalse(self.searcher.search.called)

    def test_search_deserialises_the_query_when_given_a_serialised_query(self):
        serialised_track = {
            'track_name': 'some_track_name',
            'artist_name': 'some_artist_name',
            'date_saved': 1275493486,
            'id': 'other_track_id',
            'status': 'SUCCESS',            
            'serialised_queries': {
                'combined': {
                    'id': 'some_other_id',
                    'status': 'SUCCESS',
                    'result': 'some_result',
                }
            }
        }
        deserialised_query = self.MockLastfmSearchQuery('some_other_id')
        self.searcher.deserialise.return_value = deserialised_query
        track = self.factory.deserialise(serialised_track)
        self.assertEqual(track.search['combined'], deserialised_query)

    def test_can_be_serialised_and_deserialised(self):
        serialised_track = self.track.serialise()
        track = self.factory.deserialise(serialised_track)
        self.assertEqual(track.id, self.track.id)
        self.assertEqual(track.track_name, self.track.track_name)
        self.assertEqual(track.artist_name, self.track.artist_name)
        self.assertEqual(track.date_saved, self.track.date_saved)
        self.assertEqual(track.search, self.track.search)

