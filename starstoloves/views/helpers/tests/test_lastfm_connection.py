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
def fetch_user():
    return User.objects.get(session_key='some_key')

@pytest.fixture
def fetch_connection(fetch_user, app):
    return LastfmConnectionHelper(fetch_user, app)

@pytest.fixture
def successful_connection(app, connection_with_user):
    def get_session(token):
        if (token == 'some_token'):
            return {'name': 'some_username'}
    app.auth.get_session.side_effect = get_session
    connection_with_user.connect('some_token')

@pytest.fixture
def failed_connection(app, connection_with_user):
    def get_session(token):
        if (token == 'some_token'):
            raise Exception()
    app.auth.get_session.side_effect = get_session
    connection_with_user.connect('some_token')

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
@pytest.mark.usefixtures("successful_connection")
class TestLastfmConnectionConnectSuccess():

    def test_associates_a_LastfmConnection(self, fetch_user):
        assert isinstance(fetch_user.lastfm_connection, LastfmConnection)

    def test_stores_the_username(self, fetch_connection):
        assert fetch_connection.get_username() == 'some_username'

    def test_sets_the_connection_state_as_connected(self, fetch_connection):
        assert fetch_connection.get_connection_state() == fetch_connection.CONNECTED


@pytest.mark.lastfm_only
@pytest.mark.usefixtures("failed_connection")
class TestLastfmConnectionConnectFail():

    def test_associates_a_LastfmConnection(self, fetch_user):
        assert isinstance(fetch_user.lastfm_connection, LastfmConnection)

    def test_sets_the_connection_state_as_failed(self, fetch_connection):
        assert fetch_connection.get_connection_state() == fetch_connection.FAILED


@pytest.mark.lastfm_only
@pytest.mark.usefixtures("successful_connection", "disconnected_connection")
class TestLastfmConnectionDisconnect():

    def test_there_is_no_longer_an_associated_lastfm_connection(self, fetch_user):
        with pytest.raises(LastfmConnection.DoesNotExist):
            fetch_user.lastfm_connection

    def test_the_LastfmConnection_is_deleted(self, fetch_user):
        with pytest.raises(LastfmConnection.DoesNotExist):
            LastfmConnection.objects.get(user=fetch_user)
