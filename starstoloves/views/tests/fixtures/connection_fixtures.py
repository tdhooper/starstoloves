from unittest.mock import MagicMock

import pytest

from django.test.client import Client

from starstoloves.lib.connection.lastfm_connection import LastfmConnectionHelper
from starstoloves.lib.connection.spotify_connection import SpotifyConnectionHelper


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def spotify_connection(create_patch):
    spotify_connection_repository = create_patch('starstoloves.views.connection.spotify_connection_repository')
    spotify_connection = MagicMock(spec=SpotifyConnectionHelper)
    spotify_connection_repository.from_user.return_value = spotify_connection
    return spotify_connection


@pytest.fixture
def lastfm_connection(create_patch):
    lastfm_connection_repository = create_patch('starstoloves.views.connection.lastfm_connection_repository')
    lastfm_connection = MagicMock(spec=LastfmConnectionHelper)
    lastfm_connection_repository.from_user.return_value = lastfm_connection
    return lastfm_connection


@pytest.fixture
def lastfm_connected(lastfm_connection):
    lastfm_connection.is_connected = True


@pytest.fixture
def lastfm_disconnected(lastfm_connection):
    lastfm_connection.is_connected = False


@pytest.fixture
def spotify_connected(spotify_connection):
    spotify_connection.is_connected = True


@pytest.fixture
def spotify_disconnected(spotify_connection):
    spotify_connection.is_connected = False


@pytest.fixture
def stub_get_track_mappings(create_patch):
    get_track_mappings = create_patch('starstoloves.views.main.get_track_mappings')
