from unittest.mock import patch
from unittest.mock import MagicMock
import os
import json
from urllib.parse import urlencode

from django.http import HttpResponse
from django.test import TestCase, RequestFactory

from starstoloves.views import main

class TestResultUpdate(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

        self.tracksPatcher = patch('starstoloves.views.main.get_tracks_data')
        self.tracks = self.tracksPatcher.start()

        self.renderPatcher = patch('starstoloves.views.main.render')
        self.render = self.renderPatcher.start()
        self.render.return_value = HttpResponse('somehtml')

        self.spotify_connection_repo_patcher = patch('starstoloves.views.connection.spotify_connection_repository')
        self.spotify_connection_repo = self.spotify_connection_repo_patcher.start()
        self.spotify_connection_repo.from_user.return_value.is_connected = True

        self.lastfm_connection_repo_patcher = patch('starstoloves.views.connection.lastfm_connection_repository')
        self.lastfm_connection_repo = self.lastfm_connection_repo_patcher.start()
        self.lastfm_connection_repo.from_user.return_value.is_connected = True

        script_dir = os.path.dirname(__file__)
        with open (os.path.join(script_dir, 'fixtures/results-list.json'), 'r') as results_file:
            self.results_list = json.loads(results_file.read())

        self.tracks.return_value = self.results_list

    def tearDown(self):
        self.tracksPatcher.stop()
        self.renderPatcher.stop()
        self.spotify_connection_repo_patcher.stop()
        self.lastfm_connection_repo_patcher.stop()

    def test_returns_all_search_results_by_default(self):
        response = self.makeRequest('/update-tracks')
        response_data = json.loads(response.content.decode("utf-8"))
        expected_data = [
            {'status': 'SUCCESS', 'id': '0', 'html': 'somehtml'},
            {'status': 'FAILURE', 'id': '1', 'html': 'somehtml'},
            {'status': 'SUCCESS', 'id': '2', 'html': 'somehtml'},
            {'status': 'PENDING', 'id': '3', 'html': 'somehtml'},
        ]
        self.assertEqual(response_data, expected_data)

    def test_returns_no_tracks_when_provided_state_is_unchanged(self):
        data = {
            'status[0]': 'SUCCESS',
            'status[1]': 'FAILURE',
            'status[2]': 'SUCCESS',
            'status[3]': 'PENDING',
        }
        response = self.makeRequest('/update-tracks', data)
        response_data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(response_data, [])

    def test_returns_changed_tracks_when_provided_state_is_different(self):
        data = {
            'status[0]': 'SUCCESS',
            'status[1]': 'PENDING',
            'status[2]': 'PENDING',
            'status[3]': 'PENDING',
        }
        response = self.makeRequest('/update-tracks', data)
        response_data = json.loads(response.content.decode("utf-8"))
        expected_data = [
            {'status': 'FAILURE', 'id': '1', 'html': 'somehtml'},
            {'status': 'SUCCESS', 'id': '2', 'html': 'somehtml'},
        ]
        self.assertEqual(response_data, expected_data)

    def test_returns_changed_and_missing_tracks_when_provided_state_is_different(self):
        data = {
            'status[0]': 'SUCCESS',
            'status[1]': 'PENDING',
            'status[2]': 'PENDING',
        }
        response = self.makeRequest('/update-tracks', data)
        response_data = json.loads(response.content.decode("utf-8"))
        expected_data = [
            {'status': 'FAILURE', 'id': '1', 'html': 'somehtml'},
            {'status': 'SUCCESS', 'id': '2', 'html': 'somehtml'},
            {'status': 'PENDING', 'id': '3', 'html': 'somehtml'},
        ]
        self.assertEqual(response_data, expected_data)

    def test_renders_result_as_html(self):
        data = {
            'status[0]': 'SUCCESS',
            'status[1]': 'PENDING',
            'status[2]': 'PENDING',
            'status[3]': 'PENDING',
        }
        self.makeRequest('/update-tracks', data)
        self.assertEqual(self.render.call_count, 2)
        render_args_context = [args[0][2] for args in self.render.call_args_list]
        self.assertIn({'track': self.results_list[1]}, render_args_context)
        self.assertIn({'track': self.results_list[2]}, render_args_context)

    def test_includes_rendered_result_in_returned_json(self):
        render_results = {
            '1': HttpResponse('rendered1'),
            '2': HttpResponse('rendered2')
        }
        self.render.side_effect = lambda request, template, context: render_results[context['track']['id']]
        data = {
            'status[0]': 'SUCCESS',
            'status[1]': 'PENDING',
            'status[2]': 'PENDING',
            'status[3]': 'PENDING',
        }
        response = self.makeRequest('/update-tracks', data)
        response_data = json.loads(response.content.decode("utf-8"))
        expected_data = [
            {'status': 'FAILURE', 'id': '1', 'html': 'rendered1'},
            {'status': 'SUCCESS', 'id': '2', 'html': 'rendered2'},
        ]
        self.assertEqual(response_data, expected_data)

    def makeRequest(self, url, data=None):
        if data:
            request = self.factory.post(url, data)
        else:
            request = self.factory.post(url)
        request.session_user = MagicMock()
        return main.result_update(request)

