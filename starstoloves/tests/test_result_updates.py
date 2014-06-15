from unittest.mock import patch
from unittest.mock import MagicMock
import os
import json
from urllib.parse import urlencode

from django.test import TestCase, RequestFactory

from starstoloves.views import main
from starstoloves.views.helpers.spotify_connection import SpotifyConnectionHelper

class TestResultUpdate(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.patcher = patch('starstoloves.views.main.get_tracks')
        self.tracks = self.patcher.start()

        script_dir = os.path.dirname(__file__)
        with open (os.path.join(script_dir, 'fixtures/results-list.json'), 'r') as results_file:
            self.results_list = json.loads(results_file.read())

        self.tracks.return_value = self.results_list

    def tearDown(self):
        self.patcher.stop()

    def test_returns_all_search_results_by_default(self):
        response = self.makeRequest('/update-tracks')
        response_data = json.loads(response.content.decode("utf-8"))
        expected_data = [
            {'status': 'SUCCESS', 'id': '0', 'tracks': 'sometracks'},
            {'status': 'FAILURE', 'id': '1'},
            {'status': 'SUCCESS', 'id': '2'},
            {'status': 'PENDING', 'id': '3'},
        ]
        self.assertEqual(response_data, expected_data)

    def test_returns_no_tracks_when_provided_state_is_unchanged(self):
        query = urlencode({
            'status[0]': 'SUCCESS',
            'status[1]': 'FAILURE',
            'status[2]': 'SUCCESS',
            'status[3]': 'PENDING',
        })
        response = self.makeRequest('/update-tracks?' + query)
        response_data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response_data, [])

    def test_returns_changed_tracks_when_provided_state_is_different(self):
        query = urlencode({
            'status[0]': 'SUCCESS',
            'status[1]': 'PENDING',
            'status[2]': 'PENDING',
            'status[3]': 'PENDING',
        })
        response = self.makeRequest('/update-tracks?' + query)
        response_data = json.loads(response.content.decode("utf-8"))
        expected_data = [
            {'status': 'FAILURE', 'id': '1'},
            {'status': 'SUCCESS', 'id': '2'},
        ]
        self.assertEqual(response_data, expected_data)

    def test_returns_changed_and_missing_tracks_when_provided_state_is_different(self):
        query = urlencode({
            'status[0]': 'SUCCESS',
            'status[1]': 'PENDING',
            'status[2]': 'PENDING',
        })
        response = self.makeRequest('/update-tracks?' + query)
        response_data = json.loads(response.content.decode("utf-8"))
        expected_data = [
            {'status': 'FAILURE', 'id': '1'},
            {'status': 'SUCCESS', 'id': '2'},
            {'status': 'PENDING', 'id': '3'},
        ]
        self.assertEqual(response_data, expected_data)

    def makeRequest(self, url):
        request = self.factory.get(url)
        request.spotify_connection = MagicMock(SpotifyConnectionHelper)
        return main.resultUpdate(request)

