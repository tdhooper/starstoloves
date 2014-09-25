from unittest.mock import call

import pytest

from django.core.urlresolvers import reverse

from .fixtures.connection_fixtures import *


pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures("lastfm_disconnected")
def test_index_returns_lastfm_connect_url(client):
    response = client.get('/')
    assert response.context['lfmConnectUrl'] == reverse('connect_lastfm')


@pytest.mark.usefixtures("lastfm_disconnected")
def test_index_shows_connection_failures(client, lastfm_connection):
    lastfm_connection.state = lastfm_connection.FAILED
    response = client.get('/')
    assert response.context['lfmConnectFailure'] == True


@pytest.mark.usefixtures("lastfm_connected")
def test_index_returns_lastfm_disconnect_url_when_connected(client):
    response = client.get('/')
    assert response.context['lfmDisconnectUrl'] == reverse('disconnect_lastfm')


@pytest.mark.usefixtures("lastfm_connected")
def test_index_returns_lastfm_username_when_connected(client, lastfm_connection):
    lastfm_connection.username = 'some_username'
    response = client.get('/')
    assert response.context['lfmUsername'] == 'some_username'


class TestConnectLastfm():

    @pytest.mark.usefixtures("lastfm_disconnected")
    def test_gets_the_lastfm_auth_url(self, client, lastfm_connection):
        client.get(reverse('connect_lastfm'))
        assert lastfm_connection.auth_url.call_args == call('http://testserver' + reverse('connect_lastfm'))


    @pytest.mark.usefixtures("lastfm_disconnected")
    def test_redirects_to_the_lastfm_auth(self, client, lastfm_connection):
        lastfm_connection.auth_url.return_value = 'http://some_auth_url'
        response = client.get(reverse('connect_lastfm'), follow=True)
        assert response.redirect_chain[0][0] == 'http://some_auth_url'


    @pytest.mark.usefixtures("lastfm_disconnected")
    def test_connects_when_given_a_token(self, client, lastfm_connection):
        client.get(reverse('connect_lastfm'), {'token': 'some_token'})
        assert lastfm_connection.connect.call_args == call('some_token')


    @pytest.mark.usefixtures("lastfm_disconnected")
    def test_redirects_home_when_given_a_token(self, client):
        response = client.get(reverse('connect_lastfm'), {'token': 'some_token'}, follow=True)
        assert response.redirect_chain[0][0] == 'http://testserver' + reverse('index')


    @pytest.mark.usefixtures("lastfm_connected")
    def test_redirects_home_when_already_connected(self, client):
        response = client.get(reverse('connect_lastfm'), follow=True)
        assert response.redirect_chain[0][0] == 'http://testserver' + reverse('index')


class TestDisconnectLastfm():

    def test_disconnects(self, client, lastfm_connection):
        client.get(reverse('disconnect_lastfm'))
        assert lastfm_connection.disconnect.call_count is 1


    def test_redirects_home(self, client):
        response = client.get(reverse('disconnect_lastfm'), follow=True)
        assert response.redirect_chain[0][0] == 'http://testserver' + reverse('index')
