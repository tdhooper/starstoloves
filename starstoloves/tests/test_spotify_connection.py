from unittest.mock import MagicMock

from django.test import TestCase

import spotify
from spotify import User as SpotifyUser
from spotify import Playlist

from starstoloves.models import User, SpotifyConnection
from starstoloves.views.helpers.connection import MissingUserError
from starstoloves.views.helpers.spotify_connection import SpotifyConnectionHelper


class BaseTestSpotifyConnection(TestCase):

    def setUp(self):
        self.session = MagicMock(spec=spotify.Session).return_value
        self.connection = SpotifyConnectionHelper(None, self.session)


class BaseTestSpotifyConnectionWithUser(BaseTestSpotifyConnection):

    def setUp(self):
        super().setUp()
        self.user = User(session_key='some_key')
        self.user.save()
        self.connection = SpotifyConnectionHelper(self.user, self.session)

    def tearDown(self):
        self.user.delete()


class BaseSpotifyConnectionTests():

    def test_connection_state_defaults_to_disconnected(self):
        self.assertEqual(self.connection.get_connection_state(), self.connection.DISCONNECTED)

    def test_connection_username_defaults_to_none(self):
        self.assertIsNone(self.connection.get_username())

    def test_connection_user_uri_defaults_to_none(self):
        self.assertIsNone(self.connection.get_user_uri())

    def test_connection_disconnect_is_a_noop(self):
        self.connection.disconnect()


class TestSpotifyConnectionWithoutUser(BaseTestSpotifyConnection, BaseSpotifyConnectionTests):

    def test_connect_throws(self):
        with self.assertRaises(MissingUserError):
            self.connection.connect('some_username')


class TestSpotifyConnectionWithUser(BaseTestSpotifyConnectionWithUser, BaseSpotifyConnectionTests):
    pass;


class TestSpotifyConnectionConnectSuccess(BaseTestSpotifyConnectionWithUser):

    def setUp(self):
        super().setUp()
        whenConnectSucceeds(self.session, self.connection)
        self.user = User.objects.get(session_key='some_key')
        self.connection = SpotifyConnectionHelper(self.user, self.session)

    def test_associates_a_SpotifyConnection(self):
        self.assertIsInstance(self.user.spotify_connection, SpotifyConnection)

    def test_stores_the_username(self):
        self.assertEqual(self.connection.get_username(), 'some_username')

    def test_stores_the_user_uri(self):
        self.assertEqual(self.connection.get_user_uri(), 'spotify:user:some_username')

    def test_sets_the_connection_state_as_connected(self):
        self.assertEqual(self.connection.get_connection_state(), self.connection.CONNECTED)


class TestSpotifyConnectionConnectFail(BaseTestSpotifyConnectionWithUser):

    def setUp(self):
        super().setUp()
        whenConnectFails(self.session, self.connection)
        self.user = User.objects.get(session_key='some_key')
        self.connection = SpotifyConnectionHelper(self.user, self.session)

    def test_associates_a_SpotifyConnection(self):
        self.assertIsInstance(self.user.spotify_connection, SpotifyConnection)

    def test_sets_the_connection_state_as_failed(self):
        self.assertEqual(self.connection.get_connection_state(), self.connection.FAILED)


class TestSpotifyConnectionDisconnect(BaseTestSpotifyConnectionWithUser):

    def setUp(self):
        super().setUp()
        whenConnectSucceeds(self.session, self.connection)
        self.connection.disconnect()
        self.user = User.objects.get(session_key='some_key')
        self.connection = SpotifyConnectionHelper(self.user, self.session)

    def test_there_is_no_longer_an_associated_spotify_connection(self):
        with self.assertRaises(SpotifyConnection.DoesNotExist):
            self.user.spotify_connection

    def test_the_SpotifyConnection_is_deleted(self):
        with self.assertRaises(SpotifyConnection.DoesNotExist):
            SpotifyConnection.objects.get(user=self.user)


def whenConnectSucceeds(session, connection):
    starred = MagicMock(spec=Playlist)
    starred.load.return_value = starred
    # starred.tracks_with_metadata = 'sometracks'

    user = MagicMock(spec=SpotifyUser).return_value
    user.load.return_value = user

    user.starred = starred

    def get_user(user_uri):
        if user_uri == 'spotify:user:some_username':
            return user
    session.get_user.side_effect = get_user

    connection.connect('some_username')


def whenConnectFails(session, connection):
    starred = MagicMock(spec=Playlist)
    # starred.load.return_value = starred
    # starred.tracks_with_metadata.side_effect = spotify.Error()
    starred.load.side_effect = spotify.Error()

    user = MagicMock(spec=SpotifyUser).return_value
    user.load.return_value = user

    user.starred = starred

    def get_user(user_uri):
        if user_uri == 'spotify:user:some_username':
            return user
    session.get_user.side_effect = get_user

    connection.connect('some_username')


