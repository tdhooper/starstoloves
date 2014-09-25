from unittest.mock import MagicMock, call

import pytest

from django.test.client import Client
from django.core.urlresolvers import reverse

from starstoloves.views import connection
from starstoloves.lib.connection.lastfm_connection import LastfmConnectionHelper

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def lastfm_connection(create_patch):
    lastfm_connection_repository = create_patch('starstoloves.views.connection.lastfm_connection_repository')
    lastfm_connection = MagicMock(spec=LastfmConnectionHelper)
    lastfm_connection_repository.from_user.return_value = lastfm_connection
    return lastfm_connection


def test_index_returns_lastfm_connect_url(client, lastfm_connection):
    lastfm_connection.is_connected = False
    response = client.get('/')
    assert response.context['lfmConnectUrl'] == reverse('connect_lastfm')


def test_index_shows_connection_failures(client, lastfm_connection):
    lastfm_connection.is_connected = False
    lastfm_connection.state = lastfm_connection.FAILED
    response = client.get('/')
    assert response.context['lfmConnectFailure'] == True


def test_index_returns_lastfm_disconnect_url_when_connected(client, lastfm_connection):
    lastfm_connection.is_connected = True
    response = client.get('/')
    assert response.context['lfmDisconnectUrl'] == reverse('disconnect_lastfm')


def test_index_returns_lastfm_username_when_connected(client, lastfm_connection):
    lastfm_connection.is_connected = True
    lastfm_connection.username = 'some_username'
    response = client.get('/')
    assert response.context['lfmUsername'] == 'some_username'


class TestConnectLastfm():

    def test_gets_the_lastfm_auth_url(self, client, lastfm_connection):
        lastfm_connection.is_connected = False
        client.get(reverse('connect_lastfm'))
        assert lastfm_connection.auth_url.call_args == call('http://testserver' + reverse('connect_lastfm'))


    def test_redirects_to_the_lastfm_auth(self, client, lastfm_connection):
        lastfm_connection.is_connected = False
        lastfm_connection.auth_url.return_value = 'http://some_auth_url'
        response = client.get(reverse('connect_lastfm'), follow=True)
        assert response.redirect_chain[0][0] == 'http://some_auth_url'


    def test_connects_when_given_a_token(self, client, lastfm_connection):
        lastfm_connection.is_connected = False
        client.get(reverse('connect_lastfm'), {'token': 'some_token'})
        assert lastfm_connection.connect.call_args == call('some_token')


    def test_redirects_home_when_given_a_token(self, client, lastfm_connection):
        lastfm_connection.is_connected = False
        response = client.get(reverse('connect_lastfm'), {'token': 'some_token'}, follow=True)
        assert response.redirect_chain[0][0] == 'http://testserver' + reverse('index')


    def test_redirects_home_when_already_connected(self, client, lastfm_connection):
        response = client.get(reverse('connect_lastfm'), follow=True)
        assert response.redirect_chain[0][0] == 'http://testserver' + reverse('index')


class TestDisconnectLastfm():

    def test_disconnects(self, client, lastfm_connection):
        client.get(reverse('disconnect_lastfm'))
        assert lastfm_connection.disconnect.call_count is 1


    def test_redirects_home(self, client, lastfm_connection):
        response = client.get(reverse('disconnect_lastfm'), follow=True)
        assert response.redirect_chain[0][0] == 'http://testserver' + reverse('index')
