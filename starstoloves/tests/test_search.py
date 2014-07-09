import unittest
from unittest.mock import patch
from unittest.mock import MagicMock

from starstoloves.lib.search import LastfmSearch

from celery.result import AsyncResult

class TestLastfmSearchQuery(unittest.TestCase):

    def setUp(self):
        self.async_result_patcher = patch('starstoloves.lib.search.AsyncResult', autospec=True)
        self.MockAsyncResult = self.async_result_patcher.start()
        def get_async_result(id):
            self.mock_async_result = MagicMock(spec=AsyncResult)
            self.mock_async_result.id = id
            return self.mock_async_result
        self.MockAsyncResult.side_effect = get_async_result

        self.revoke_patcher = patch('starstoloves.lib.search.revoke')
        self.revoke = self.revoke_patcher.start()

        self.search_patcher = patch('starstoloves.lib.search.search_lastfm')
        search_lastfm = self.search_patcher.start()
        search_lastfm_async_result = MagicMock(spec=AsyncResult).return_value
        search_lastfm_async_result.id = 'some_id'
        search_lastfm.delay.return_value = search_lastfm_async_result

        self.searcher = LastfmSearch('some_lastfm_app')
        self.query = self.searcher.search('track_name', 'artist_name')

    def tearDown(self):
        self.async_result_patcher.stop()
        self.revoke_patcher.stop()
        self.search_patcher.stop()

    def test_has_an_id(self):
        self.assertEqual(self.query.id, 'some_id')

    def test_status_is_result_status(self):
        self.mock_async_result.status = 'SOME_STATUS'
        self.assertEqual(self.query.status, 'SOME_STATUS')

    def test_result_doesnt_have_tracks_when_not_ready(self):
        self.mock_async_result.ready = MagicMock(return_value=False)
        self.assertFalse(self.query.result)

    def test_result_doesnt_have_tracks_when_ready_but_no_results(self):
        result_data = {
            'trackmatches': "\n"
        }
        self.mock_async_result.ready = MagicMock(return_value=True)
        self.mock_async_result.info = result_data
        self.assertFalse(self.query.result)

    def test_result_has_tracks_when_ready(self):
        result_data = {
            'trackmatches': {
                'track': [
                    {
                        'name': 'trackA',
                        'artist': 'artistA',
                        'url': 'urlA',
                    },{
                        'name': 'trackB',
                        'artist': 'artistB',
                        'url': 'urlB',
                    },
                ]
            }
        }
        expected_tracks = [
            {
                'track_name': 'trackA',
                'artist_name': 'artistA',
                'url': 'urlA',
            },{
                'track_name': 'trackB',
                'artist_name': 'artistB',
                'url': 'urlB',
            },
        ]
        self.mock_async_result.ready = MagicMock(return_value=True)
        self.mock_async_result.info = result_data
        self.assertEqual(self.query.result, expected_tracks)

    def test_result_has_tracks_when_ready_and_there_is_only_one_result(self):
        result_data = {
            'trackmatches': {
                'track': {
                    'name': 'trackA',
                    'artist': 'artistA',
                    'url': 'urlA',
                }
            }
        }
        expected_tracks = [{
            'track_name': 'trackA',
            'artist_name': 'artistA',
            'url': 'urlA'
        }]
        self.mock_async_result.ready = MagicMock(return_value=True)
        self.mock_async_result.info = result_data
        self.assertEqual(self.query.result, expected_tracks)

    def test_data_doesnt_have_tracks_when_ready_and_result_is_error(self):
        self.mock_async_result.ready = MagicMock(return_value=True)
        self.mock_async_result.info = TypeError
        self.assertFalse(self.query.result)

    def test_stops_the_task_when_requested(self):
        self.mock_async_result.id = 'some_id'
        self.query.stop()
        self.revoke.assert_called_with('some_id')

    def test_can_be_serialised(self):
        self.mock_async_result.status = 'SOME_STATUS'
        result_data = {
            'trackmatches': {
                'track': {
                    'name': 'trackA',
                    'artist': 'artistA',
                    'url': 'urlA',
                }
            }
        }
        self.mock_async_result.ready = MagicMock(return_value=True)
        self.mock_async_result.info = result_data
        expected = {
            'id': 'some_id',
            'status': 'SOME_STATUS',
            'result': [{
                'track_name': 'trackA',
                'artist_name': 'artistA',
                'url': 'urlA'
            }],
        }
        self.assertEqual(self.query.serialise(), expected)

    def test_pending_query_can_be_deserialised_and_will_update(self):
        serialised = {
            'id': 'some_id',
            'status': 'PENDING',
            'result': None,
        }
        query = self.searcher.deserialise(serialised)
        result_data = {
            'trackmatches': {
                'track': {
                    'name': 'trackA',
                    'artist': 'artistA',
                    'url': 'urlA',
                }
            }
        }
        self.mock_async_result.ready = MagicMock(return_value=True)
        self.mock_async_result.info = result_data
        self.mock_async_result.status = 'SUCCESS'
        expected_tracks = [{
            'track_name': 'trackA',
            'artist_name': 'artistA',
            'url': 'urlA'
        }]
        self.assertEqual(query.id, 'some_id')
        self.assertEqual(query.status, 'SUCCESS')
        self.assertEqual(query.result, expected_tracks)

    def test_sucessful_query_can_be_deserialised(self):
        serialised = {
            'id': 'some_id',
            'status': 'SUCCESS',
            'result': 'some_result',
        }
        query = self.searcher.deserialise(serialised)
        self.assertEqual(query.id, 'some_id')
        self.assertEqual(query.status, 'SUCCESS')
        self.assertEqual(query.result, 'some_result')
    
    def test_failed_query_can_be_deserialised(self):
        serialised = {
            'id': 'some_id',
            'status': 'FAILURE',
            'result': None,
        }
        query = self.searcher.deserialise(serialised)
        self.assertEqual(query.id, 'some_id')
        self.assertEqual(query.status, 'FAILURE')
        self.assertEqual(query.result, None)

    def test_doesnt_create_an_AsyncResult_when_deserialising_a_successful_query(self):
        serialised = {
            'id': 'some_id',
            'status': 'SUCCESS',
            'result': 'some_result',
        }
        query = self.searcher.deserialise(serialised)
        self.assertEqual(self.MockAsyncResult.call_count, 1)

    def test_doesnt_create_an_AsyncResult_when_deserialising_a_failed_query(self):
        serialised = {
            'id': 'some_id',
            'status': 'FAILURE',
            'result': None,
        }
        query = self.searcher.deserialise(serialised)
        self.assertEqual(self.MockAsyncResult.call_count, 1)


from starstoloves.lib.search import LastfmSearchQueryWithLoves

class TestLastfmSearchQueryWithLoves(unittest.TestCase):

    def setUp(self):
        self.patcher = patch('starstoloves.lib.search.AsyncResult', autospec=True)
        self.MockAsyncResult = self.patcher.start()
        self.mock_async_result = self.MockAsyncResult.return_value
        self.loved_tracks_urls = ['urlA', 'urlC']
        self.query = LastfmSearchQueryWithLoves('some_id', self.loved_tracks_urls)

    def tearDown(self):
        self.patcher.stop()

    def test_result_tracks_are_marked_as_loved_when_they_match_a_loved_track(self):
        result_data = {
            'trackmatches': {
                'track': [
                    {
                        'name': 'trackA',
                        'artist': 'artistA',
                        'url': 'urlA',
                    },{
                        'name': 'trackB',
                        'artist': 'artistB',
                        'url': 'urlB',
                    },
                ]
            }
        }
        expected_tracks = [
            {
                'track_name': 'trackA',
                'artist_name': 'artistA',
                'url': 'urlA',
                'loved': True,
            },{
                'track_name': 'trackB',
                'artist_name': 'artistB',
                'url': 'urlB',
                'loved': False,
            },
        ]
        self.mock_async_result.ready = MagicMock(return_value=True)
        self.mock_async_result.info = result_data
        self.assertEqual(self.query.result, expected_tracks)

