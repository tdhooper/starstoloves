from unittest.mock import MagicMock

import pytest

from lastfm import lfm

from starstoloves.models import User, LastfmConnection
from starstoloves.views.helpers.connection import MissingUserError
from starstoloves.views.helpers.lastfm_connection import LastfmConnectionHelper

from .fixtures.connection_fixtures import *


pytestmark = pytest.mark.django_db

@pytest.fixture
def app(fixtures):
    return fixtures.app

@pytest.fixture
def disconnected_connection(app, connection_with_user):
    connection_with_user.disconnect()


@pytest.mark.lastfm_only
def test_get_auth_url_proxies_to_app(connection, app):
    def get_url(callback_url):
        if (callback_url == 'some_callback'):
            return 'some_auth_url'
    app.auth.get_url.side_effect = get_url
    auth_url = connection.get_auth_url('some_callback')
    assert auth_url == 'some_auth_url'


@pytest.mark.lastfm_only
@pytest.mark.usefixtures("successful_connection", "disconnected_connection")
class TestLastfmConnectionDisconnect():

    def test_there_is_no_longer_an_associated_lastfm_connection(self, fetch_user):
        with pytest.raises(LastfmConnection.DoesNotExist):
            fetch_user.lastfm_connection

    def test_the_LastfmConnection_is_deleted(self, fetch_user):
        with pytest.raises(LastfmConnection.DoesNotExist):
            LastfmConnection.objects.get(user=fetch_user)
