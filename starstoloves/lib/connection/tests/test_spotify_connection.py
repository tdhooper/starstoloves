from unittest.mock import MagicMock

import pytest

from .fixtures.connection_fixtures import *


pytestmark = pytest.mark.django_db

@pytest.mark.spotify_only
def test_connection_token_defaults_to_none(connection):
    assert connection.token is None


@pytest.mark.spotify_only
@pytest.mark.usefixtures("successful_connection")
class TestSpotifyConnectionConnectSuccess():

    def test_stores_the_token(self, fetch_connection):
        assert fetch_connection().token == 'some_spotify_token'
