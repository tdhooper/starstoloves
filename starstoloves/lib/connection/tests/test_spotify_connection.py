from unittest.mock import MagicMock

import pytest

from spotipy.oauth2 import SpotifyOAuth

from .fixtures.connection_fixtures import *


pytestmark = pytest.mark.django_db



@pytest.fixture
def auth(fixtures):
    auth = MagicMock(spec=SpotifyOAuth).return_value
    def SpotifyOAuth_instance(client_id, client_secret, redirect_uri, scope):
        if redirect_uri == 'some_callback_url':
            return auth
    fixtures.SpotifyOAuth.side_effect = SpotifyOAuth_instance
    return auth


@pytest.mark.spotify_only
def test_get_auth_url_proxies_to_api(connection, auth):
    auth.get_authorize_url.return_value = 'some_auth_url'
    assert connection.auth_url('some_callback_url') == 'some_auth_url'


@pytest.mark.spotify_only
def test_connection_token_defaults_to_none(connection):
    assert connection.token is None


@pytest.mark.spotify_only
@pytest.mark.usefixtures("successful_connection")
class TestSpotifyConnectionConnectSuccess():

    def test_stores_the_token(self, fetch_connection):
        assert fetch_connection().token == 'some_spotify_token'
