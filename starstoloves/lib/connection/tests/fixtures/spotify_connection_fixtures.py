from unittest.mock import MagicMock

import pytest

import spotify
from spotify import User as SpotifyUser
from spotify import Playlist

from starstoloves.models import SpotifyConnection
from starstoloves.lib.connection.spotify_connection import SpotifyConnectionHelper

from .common_connection_fixtures import CommonConnectionFixtures


class SpotifyConnectionFixtures(CommonConnectionFixtures):

    connection_name = 'spotify_connection'
    connection_class = SpotifyConnection

    def __init__(self):
        super().__init__()
        self.session = MagicMock(spec=spotify.Session).return_value

    @property
    def connection_without_user(self):
        return SpotifyConnectionHelper(None, self.session)

    @property
    def connection_with_user(self):
        return SpotifyConnectionHelper(self.user, self.session)

    @property
    def fetch_connection(self):
        return SpotifyConnectionHelper(self.fetch_user, self.session)

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

        self.connection_with_user.connect('some_username')

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

        self.connection_with_user.connect('some_username')
