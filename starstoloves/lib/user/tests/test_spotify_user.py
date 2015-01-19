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


def test_api_creates_api_instance_with_token(spotify_user, spotify_connection, Spotify_patch):
    spotify_connection.token = 'some_token'
    assert spotify_user.api is Spotify_patch.return_value
    assert Spotify_patch.call_args == call(auth='some_token')



class TestStarredTracks:

    def test_starred_tracks_loads_the_users_starred_tracks(self, spotify_user, spotify_api, spotify_connection):
        spotify_connection.username = 'some_user'
        spotify_user.starred_tracks
        assert spotify_api.user_playlist.call_args == call('some_user')


    @pytest.mark.usefixtures("spotify_user_with_starred")
    def test_starred_tracks_returns_the_users_starred_tracks(self, spotify_user):
        assert spotify_user.starred_tracks == [
            {
                'track_name': 'some_track',
                'artist_name': 'some_artist',
                'date_saved': 123456,
            },{
                'track_name': 'another_track',
                'artist_name': 'another_artist',
                'date_saved': 789012,
            }
        ]


    @pytest.mark.usefixtures("spotify_user_with_multiple_starred_pages")
    def test_starred_tracks_gets_all_pages(self, spotify_user):
        assert spotify_user.starred_tracks == [
            {
                'track_name': 'some_track',
                'artist_name': 'some_artist',
                'date_saved': 123456,
            },{
                'track_name': 'another_track',
                'artist_name': 'another_artist',
                'date_saved': 789012,
            },{
                'track_name': 'other_track',
                'artist_name': 'other_artist',
                'date_saved': 1273801872,
            }
        ]
