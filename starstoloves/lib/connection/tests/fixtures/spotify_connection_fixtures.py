from unittest.mock import MagicMock, patch

import pytest

import spotipy

from starstoloves.models import SpotifyConnection
from starstoloves.lib.connection.spotify_connection import SpotifyConnectionHelper

from .common_connection_fixtures import CommonConnectionFixtures
from ... import spotify_connection_repository


class SpotifyConnectionFixtures(CommonConnectionFixtures):

    connection_name = 'spotify_connection'
    connection_class = SpotifyConnection

    def __init__(self):
        super().__init__()
        self.spotipy_auth_patcher = patch('starstoloves.lib.connection.spotify_connection_repository.SpotifyOAuth', autospec=True)
        self.spotipy_api_patcher = patch('starstoloves.lib.connection.spotify_connection.Spotify', autospec=True)
        self.spotipy_auth = self.spotipy_auth_patcher.start().return_value
        self.Spotify = self.spotipy_api_patcher.start()

    def finalizer(self):
        self.spotipy_auth_patcher.stop()
        self.spotipy_api_patcher.stop()
        super().finalizer()

    @property
    def connection(self):
        return spotify_connection_repository.from_user(self.user, 'some_callback_url')

    @property
    def fetch_connection(self):
        def fetch():
            return spotify_connection_repository.from_user(self.user, 'some_callback_url')
        return fetch

    def successful_connection(self):
        def get_access_token(response_code):
            if response_code == 'some_response_code':
                return {
                    'access_token': 'some_spotify_token'
                }
        self.spotipy_auth.get_access_token.side_effect = get_access_token

        def get_api_instance(auth=None):
            if auth == 'some_spotify_token':
                return self.Spotify.return_value
        self.Spotify.side_effect = get_api_instance
        self.Spotify.return_value.me.return_value = {'id': 'some_username'}

        self.connection.connect('some_response_code')


    def failed_connection(self):
        self.spotipy_auth.get_access_token.side_effect = spotipy.oauth2.SpotifyOauthError
        self.connection.connect('some_response_code')

