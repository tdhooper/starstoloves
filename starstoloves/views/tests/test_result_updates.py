from unittest.mock import patch
from unittest.mock import MagicMock
import os
import json
from urllib.parse import urlencode

from django.http import HttpResponse
from django.test import TestCase, RequestFactory

from starstoloves.lib.track.spotify_track import SpotifyTrack
from starstoloves.views import main



spotify_tracks = [
    SpotifyTrack(
        artist_name="Modeselektor",
        track_name="Das Claudia Woelky Massaker"
    ),
    SpotifyTrack(
        artist_name="The Bloody Beetroots",
        track_name="It’s Better A DJ On 2 turntables"
    ),
    SpotifyTrack(
        artist_name="A.S.Y.S.",
        track_name="No More Fucking Rock´n´ Roll"
    ),
    SpotifyTrack(
        artist_name="Booka Shade",
        track_name="No Difference"
    ),
]

query_dicts = {
    "Das Claudia Woelky Massaker": {
        "id": "0",
        "status": "SUCCESS",
    },
    "It’s Better A DJ On 2 turntables": {
        "id": "1",
        "status": "FAILURE",
    },
    "No More Fucking Rock´n´ Roll": {
        "id": "2",
        "status": "SUCCESS",
    },
    "No Difference": {
        "id": "3",
        "status": "PENDING",
    },
}



class TestResultUpdate(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

        self.LastfmQuery_patcher = patch('starstoloves.lib.search.query_repository.LastfmQuery')
        self.LastfmQuery_patch = self.LastfmQuery_patcher.start()
        def new_LastfmQuery(repository, track_name, artist_name=None, async_result=None, results=None):
            query_dict = query_dicts[track_name]
            query = MagicMock()
            query.id = query_dict['id']
            query.status = query_dict['status']
            return query
        self.LastfmQuery_patch.side_effect = new_LastfmQuery

        self.renderPatcher = patch('starstoloves.views.main.render')
        self.render = self.renderPatcher.start()
        self.render.return_value = HttpResponse('somehtml')

        self.spotify_connection_repo_patcher = patch('starstoloves.views.connection.spotify_connection_repository')
        self.spotify_connection_repo = self.spotify_connection_repo_patcher.start()
        self.spotify_connection_repo.from_user.return_value.is_connected = True

        self.lastfm_connection_repo_patcher = patch('starstoloves.views.connection.lastfm_connection_repository')
        self.lastfm_connection_repo = self.lastfm_connection_repo_patcher.start()
        self.lastfm_connection_repo.from_user.return_value.is_connected = True


    def tearDown(self):
        self.LastfmQuery_patcher.stop()
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
        assert render_args_context[0]['mapping'].track == spotify_tracks[1]
        assert render_args_context[1]['mapping'].track == spotify_tracks[2]


    def test_includes_rendered_result_in_returned_json(self):
        render_results = {
            '1': HttpResponse('rendered1'),
            '2': HttpResponse('rendered2')
        }
        self.render.side_effect = lambda request, template, context: render_results[context['mapping'].id]
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

        user = MagicMock()
        user.starred_tracks = spotify_tracks
        request.session_user = user

        return main.result_update(request)

