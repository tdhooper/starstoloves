from unittest.mock import MagicMock

import pytest

from lastfm import lfm

from starstoloves.models import User, LastfmConnection
from starstoloves.views.helpers.connection import MissingUserError
from starstoloves.views.helpers.lastfm_connection import LastfmConnectionHelper

pytestmark = pytest.mark.django_db

@pytest.fixture
def app():
    return MagicMock(spec=lfm.App).return_value

@pytest.fixture
def user(request):
    user = User(session_key='some_key')
    user.save()
    def fin():
        user.delete()
    request.addfinalizer(fin)
    return user

@pytest.fixture
def connection_without_user(request, app):
    return LastfmConnectionHelper(None, app)

@pytest.fixture
def connection_with_user(request, user, app):
    return LastfmConnectionHelper(user, app)

@pytest.fixture(params=[True, False])
def connection(request, user, app):
    if (request.param):
        return LastfmConnectionHelper(user, app)
    else:
        return LastfmConnectionHelper(None, app)

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


def test_state_defaults_to_disconnected(connection):
    assert connection.get_connection_state() == connection.DISCONNECTED

def test_username_defaults_to_none(connection):
    assert connection.get_username() is None

def test_disconnect_is_a_noop(connection):
    connection.disconnect()

def test_get_auth_url_proxies_to_app(connection, app):
    def get_url(callback_url):
        if (callback_url == 'some_callback'):
            return 'some_auth_url'
    app.auth.get_url.side_effect = get_url
    auth_url = connection.get_auth_url('some_callback')
    assert auth_url == 'some_auth_url'

def test_connect_throws(connection_without_user):
    with pytest.raises(MissingUserError):
        connection_without_user.connect('some_token')


@pytest.mark.usefixtures("successful_connection")
class TestLastfmConnectionConnectSuccess():

    def test_associates_a_LastfmConnection(self, fetch_user):
        assert isinstance(fetch_user.lastfm_connection, LastfmConnection)

    def test_stores_the_username(self, fetch_connection):
        assert fetch_connection.get_username() == 'some_username'

    def test_sets_the_connection_state_as_connected(self, fetch_connection):
        assert fetch_connection.get_connection_state() == fetch_connection.CONNECTED


@pytest.mark.usefixtures("failed_connection")
class TestLastfmConnectionConnectFail():

    def test_associates_a_LastfmConnection(self, fetch_user):
        assert isinstance(fetch_user.lastfm_connection, LastfmConnection)

    def test_sets_the_connection_state_as_failed(self, fetch_connection):
        assert fetch_connection.get_connection_state() == fetch_connection.FAILED


@pytest.mark.usefixtures("successful_connection", "disconnected_connection")
class TestLastfmConnectionDisconnect():

    def test_there_is_no_longer_an_associated_lastfm_connection(self, fetch_user):
        with pytest.raises(LastfmConnection.DoesNotExist):
            fetch_user.lastfm_connection

    def test_the_LastfmConnection_is_deleted(self, fetch_user):
        with pytest.raises(LastfmConnection.DoesNotExist):
            LastfmConnection.objects.get(user=fetch_user)
