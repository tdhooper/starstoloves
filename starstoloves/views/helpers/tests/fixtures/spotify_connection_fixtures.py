from unittest.mock import MagicMock

import pytest

import spotify

from starstoloves.views.helpers.spotify_connection import SpotifyConnectionHelper

from .common_connection_fixtures import CommonConnectionFixtures


class SpotifyConnectionFixtures(CommonConnectionFixtures):

    def __init__(self):
        super().__init__()
        self.session = MagicMock(spec=spotify.Session).return_value

    @property
    def connection_without_user(self):
        return SpotifyConnectionHelper(None, self.session)

    @property
    def connection_with_user(self):
        return SpotifyConnectionHelper(self.user, self.session)
