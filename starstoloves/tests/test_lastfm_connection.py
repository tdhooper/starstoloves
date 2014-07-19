from unittest.mock import MagicMock

from django.test import TestCase

from lastfm import lfm

from starstoloves.models import User, LastfmConnection
from starstoloves.views.helpers.connection import MissingUserError
from starstoloves.views.helpers.lastfm_connection import LastfmConnectionHelper


class BaseTestLastfmConnection(TestCase):

    def setUp(self):
        self.app = MagicMock(spec=lfm.App).return_value
        self.connection = LastfmConnectionHelper(None, self.app)


class BaseTestLastfmConnectionWithUser(BaseTestLastfmConnection):

    def setUp(self):
        super().setUp()
        self.user = User(session_key='some_key')
        self.user.save()
        self.connection = LastfmConnectionHelper(self.user, self.app)

    def tearDown(self):
        self.user.delete()


class BaseLastfmConnectionTests():

    def test_connection_state_defaults_to_disconnected(self):
        self.assertEqual(self.connection.get_connection_state(), self.connection.DISCONNECTED)

    def test_connection_username_defaults_to_none(self):
        self.assertIsNone(self.connection.get_username())

    def test_connection_disconnect_is_a_noop(self):
        self.connection.disconnect()

    def test_get_auth_url_proxies_to_app(self):
        def get_url(callback_url):
            if (callback_url == 'some_callback'):
                return 'some_auth_url'
        self.app.auth.get_url.side_effect = get_url
        auth_url = self.connection.get_auth_url('some_callback')
        self.assertEqual(auth_url, 'some_auth_url')


class TestLastfmConnectionWithoutUser(BaseTestLastfmConnection, BaseLastfmConnectionTests):

    def test_connect_throws(self):
        with self.assertRaises(MissingUserError):
            self.connection.connect('some_token')


class TestLastfmConnectionWithUser(BaseTestLastfmConnectionWithUser, BaseLastfmConnectionTests):
    pass;


class TestLastfmConnectionConnectSuccess(BaseTestLastfmConnectionWithUser):

    def setUp(self):
        super().setUp()
        whenConnectSucceeds(self.app, self.connection)
        self.user = User.objects.get(session_key='some_key')
        self.connection = LastfmConnectionHelper(self.user, self.app)

    def test_associates_a_LastfmConnection(self):
        self.assertIsInstance(self.user.lastfm_connection, LastfmConnection)

    def test_stores_the_username(self):
        self.assertEqual(self.connection.get_username(), 'some_username')

    def test_sets_the_connection_state_as_connected(self):
        self.assertEqual(self.connection.get_connection_state(), self.connection.CONNECTED)


class TestLastfmConnectionConnectFail(BaseTestLastfmConnectionWithUser):

    def setUp(self):
        super().setUp()
        whenConnectFails(self.app, self.connection)
        self.user = User.objects.get(session_key='some_key')
        self.connection = LastfmConnectionHelper(self.user, self.app)

    def test_associates_a_LastfmConnection(self):
        self.assertIsInstance(self.user.lastfm_connection, LastfmConnection)

    def test_sets_the_connection_state_as_failed(self):
        self.assertEqual(self.connection.get_connection_state(), self.connection.FAILED)


class TestLastfmConnectionDisconnect(BaseTestLastfmConnectionWithUser):

    def setUp(self):
        super().setUp()
        whenConnectSucceeds(self.app, self.connection)
        self.connection.disconnect()
        self.user = User.objects.get(session_key='some_key')
        self.connection = LastfmConnectionHelper(self.user, self.app)

    def test_there_is_no_longer_an_associated_lastfm_connection(self):
        with self.assertRaises(LastfmConnection.DoesNotExist):
            self.user.lastfm_connection

    def test_the_LastfmConnection_is_deleted(self):
        with self.assertRaises(LastfmConnection.DoesNotExist):
            LastfmConnection.objects.get(user=self.user)


def whenConnectSucceeds(app, connection):
    def get_session(token):
        if (token == 'some_token'):
            return {'name': 'some_username'}
    app.auth.get_session.side_effect = get_session
    connection.connect('some_token')


def whenConnectFails(app, connection):
    def get_session(token):
        if (token == 'some_token'):
            raise Exception()
    app.auth.get_session.side_effect = get_session
    connection.connect('some_token')

