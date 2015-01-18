from unittest.mock import MagicMock, patch

import pytest

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth, SpotifyOauthError

from starstoloves.models import SpotifyConnection
from starstoloves.lib.connection.spotify_connection import SpotifyConnectionHelper

from .common_connection_fixtures import CommonConnectionFixtures
from ... import spotify_connection_repository


class SpotifyConnectionFixtures(CommonConnectionFixtures):

    connection_name = 'spotify_connection'
    connection_class = SpotifyConnection

    def __init__(self):
        super().__init__()
        self.spotipy_auth_patcher = patch('starstoloves.lib.connection.spotify_connection.SpotifyOAuth', autospec=True)
        self.spotipy_api_patcher = patch('starstoloves.lib.connection.spotify_connection.Spotify', autospec=True)
        self.SpotifyOAuth = self.spotipy_auth_patcher.start()
        self.Spotify = self.spotipy_api_patcher.start()

    def finalizer(self):
        self.spotipy_auth_patcher.stop()
        self.spotipy_api_patcher.stop()
        super().finalizer()

    @property
    def connection(self):
        return spotify_connection_repository.from_user(self.user)

    @property
    def fetch_connection(self):
        def fetch():
            return spotify_connection_repository.from_user(self.user)
        return fetch

    def successful_connection(self):

        auth = MagicMock(spec=SpotifyOAuth).return_value
        def SpotifyOAuth_instance(client_id, client_secret, redirect_uri):
            if redirect_uri == 'some_callback_url':
                return auth
        self.SpotifyOAuth.side_effect = SpotifyOAuth_instance

        def get_access_token(response_code):
            if response_code == 'some_response_code':
                return {
                    'access_token': 'some_spotify_token'
                }
        auth.get_access_token.side_effect = get_access_token

        spotify = MagicMock(spec=Spotify).return_value
        def Spotify_instance(auth=None):
            if auth == 'some_spotify_token':
                return spotify
        self.Spotify.side_effect = Spotify_instance

        spotify.me.return_value = {'id': 'some_username'}

        self.connection.connect('some_response_code', 'some_callback_url')


    def failed_connection(self):
        self.SpotifyOAuth.return_value.get_access_token.side_effect = SpotifyOauthError
        self.connection.connect('some_response_code', 'some_callback_url')

