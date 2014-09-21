from unittest.mock import MagicMock, patch

import pytest

import spotify
from spotify import User as SpotifyUser
from spotify import Playlist

from starstoloves.models import SpotifyConnection
from starstoloves.lib.connection.spotify_connection import SpotifyConnectionHelper

from .common_connection_fixtures import CommonConnectionFixtures
from ... import spotify_connection_repository


class SpotifyConnectionFixtures(CommonConnectionFixtures):

    connection_name = 'spotify_connection'
    connection_class = SpotifyConnection

    def __init__(self):
        super().__init__()
        self.session_patch = patch('starstoloves.lib.connection.spotify_connection_repository.spotify_session')
        self.session = self.session_patch.start()

    def finalizer(self):
        self.session_patch.stop()
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
        starred = MagicMock(spec=Playlist)
        starred.load.return_value = starred
        # starred.tracks_with_metadata = 'sometracks'

        user = MagicMock(spec=SpotifyUser).return_value
        user.load.return_value = user

        user.starred = starred

        def get_user(user_uri):
            if user_uri == 'spotify:user:some_username':
                return user
        self.session.get_user.side_effect = get_user

        self.connection.connect('some_username')

    def failed_connection(self):
        starred = MagicMock(spec=Playlist)
        # starred.load.return_value = starred
        # starred.tracks_with_metadata.side_effect = spotify.Error()
        starred.load.side_effect = spotify.Error()

        user = MagicMock(spec=SpotifyUser).return_value
        user.load.return_value = user

        user.starred = starred

        def get_user(user_uri):
            if user_uri == 'spotify:user:some_username':
                return user
        self.session.get_user.side_effect = get_user

        self.connection.connect('some_username')
