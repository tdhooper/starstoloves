from unittest.mock import MagicMock, call

import pytest

from ..spotify_user import SpotifyUser
from .fixtures.spotify_user_fixtures import *
from starstoloves.lib.connection.spotify_connection import SpotifyConnectionHelper

pytestmark = pytest.mark.django_db

@pytest.fixture
def spotify_connection(create_patch):
    return MagicMock(spec=SpotifyConnectionHelper).return_value

@pytest.fixture
def spotify_user(spotify_connection):
    return SpotifyUser(spotify_connection)

@pytest.mark.usefixtures("spotify_user_with_starred", "spotify_session")
class TestStarredTracks:

    def test_starred_tracks_loads_the_user(self, spotify_user, spotify_session, spotify_connection):
        spotify_user.starred_tracks
        assert spotify_session.get_user.call_args == call(spotify_connection.user_uri)
        assert spotify_session.get_user.return_value.load.call_count is 1

    @pytest.mark.usefixtures("spotify_user_with_starred")
    def test_starred_tracks_loads_the_users_starred_tracks(self, spotify_user, playlist):
        spotify_user.starred_tracks
        assert playlist.load.call_count is 1

    def test_starred_tracks_returns_the_users_starred_tracks(self, spotify_user):
        assert spotify_user.starred_tracks == track_data_list
