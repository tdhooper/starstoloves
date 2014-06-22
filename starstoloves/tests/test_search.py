import unittest
from unittest.mock import patch
from unittest.mock import MagicMock

from starstoloves.lib.search import LastfmSearchResult

from celery.result import AsyncResult

class TestLastfmSearchResult(unittest.TestCase):

    def setUp(self):
        self.async_result_patcher = patch('starstoloves.lib.search.AsyncResult', autospec=True)
        self.revoke_patcher = patch('starstoloves.lib.search.revoke')
        self.MockAsyncResult = self.async_result_patcher.start()
        self.revoke = self.revoke_patcher.start()
        self.mock_async_result = self.MockAsyncResult.return_value
        self.result = LastfmSearchResult('some_id')

    def tearDown(self):
        self.async_result_patcher.stop()
        self.revoke_patcher.stop()

    def test_data_fetches_the_async_result(self):
        self.MockAsyncResult.assert_called_with('some_id')

    def test_data_has_an_id(self):
        self.mock_async_result.id = 'some_id'
        self.assertEqual(self.result.data['id'], 'some_id')

    def test_data_has_a_status(self):
        self.mock_async_result.status = 'SOME_STATUS'
        self.assertEqual(self.result.data['status'], 'SOME_STATUS')

    def test_data_doesnt_have_tracks_when_not_ready(self):
        self.mock_async_result.ready = MagicMock(return_value=False)
        self.assertFalse('tracks' in self.result.data)

    def test_data_doesnt_have_tracks_when_ready_but_no_results(self):
        result_data = {
            'trackmatches': "\n"
        }
        self.mock_async_result.ready = MagicMock(return_value=True)
        self.mock_async_result.info = result_data
        self.assertFalse('tracks' in self.result.data)

    def test_data_has_tracks_when_ready(self):
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
        self.assertEqual(self.result.data['tracks'], expected_tracks)

    def test_data_has_tracks_when_ready_and_there_is_only_one_result(self):
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
        self.assertEqual(self.result.data['tracks'], expected_tracks)

    def test_data_doesnt_have_tracks_when_ready_and_result_is_error(self):
        self.mock_async_result.ready = MagicMock(return_value=True)
        self.mock_async_result.info = TypeError
        self.assertFalse('tracks' in self.result.data)

    def test_stops_the_task_when_requested(self):
        self.mock_async_result.id = 'some_id'
        self.result.stop()
        self.revoke.assert_called_with('some_id')


from starstoloves.lib.search import LastfmSearchResultWithLoves

class TestLastfmSearchResultWithLoves(unittest.TestCase):

    def setUp(self):
        self.patcher = patch('starstoloves.lib.search.AsyncResult', autospec=True)
        self.MockAsyncResult = self.patcher.start()
        self.mock_async_result = self.MockAsyncResult.return_value
        self.loved_tracks_urls = ['urlA', 'urlC']
        self.result = LastfmSearchResultWithLoves('some_id', self.loved_tracks_urls)

    def tearDown(self):
        self.patcher.stop()

    def test_data_tracks_are_marked_as_loved_when_they_match_a_loved_track(self):
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
        self.assertEqual(self.result.data['tracks'], expected_tracks)

