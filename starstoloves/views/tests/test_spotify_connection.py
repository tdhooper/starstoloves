from unittest.mock import call

import pytest

from django.core.urlresolvers import reverse

from starstoloves.forms import SpotifyConnectForm

from .fixtures.connection_fixtures import *


pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures("lastfm_disconnected")
@pytest.mark.usefixtures("spotify_disconnected")
def test_index_returns_no_spotify_form_when_lastfm_is_not_connected(client, spotify_connection):
    response = client.get('/')
    assert 'spForm' not in response.context


@pytest.mark.usefixtures("lastfm_connected")
@pytest.mark.usefixtures("spotify_disconnected")
def test_index_returns_spotify_form(client, spotify_connection):
    response = client.get('/')
    assert isinstance(response.context['spForm'], SpotifyConnectForm)
    assert response.context['spConnectUrl'] == reverse('index')


@pytest.mark.usefixtures("lastfm_connected")
@pytest.mark.usefixtures("spotify_connected")
@pytest.mark.usefixtures("stub_get_track_mappings")
def test_index_returns_spotify_disconnect_url_when_connected(client):
    response = client.get('/')
    assert response.context['spDisconnectUrl'] == reverse('disconnect_spotify')


@pytest.mark.usefixtures("lastfm_connected")
@pytest.mark.usefixtures("spotify_connected")
@pytest.mark.usefixtures("stub_get_track_mappings")
def test_index_returns_spotify_username_when_connected(client, spotify_connection):
    spotify_connection.username = 'some_username'
    response = client.get('/')
    assert response.context['spUsername'] == 'some_username'


@pytest.mark.usefixtures("lastfm_connected")
@pytest.mark.usefixtures("stub_get_track_mappings")
class TestConnectSpotify():

    @pytest.mark.usefixtures("spotify_disconnected")
    def test_gets_the_lastfm_auth_url(self, client, spotify_connection):
        client.get(reverse('connect_spotify'))
        assert spotify_connection.auth_url.call_args == call('http://testserver' + reverse('connect_spotify'))


    @pytest.mark.usefixtures("spotify_disconnected")
    def test_redirects_to_the_spotify_auth(self, client, spotify_connection):
        spotify_connection.auth_url.return_value = 'http://some_auth_url'
        response = client.get(reverse('connect_spotify'), follow=True)
        assert response.redirect_chain[0][0] == 'http://some_auth_url'


    @pytest.mark.usefixtures("spotify_disconnected")
    def test_connects_when_given_a_code(self, client, spotify_connection):
        client.get(reverse('connect_spotify'), {'code': 'some_code'})
        assert spotify_connection.connect.call_args == call('some_code', 'http://testserver' + reverse('connect_spotify'))


    @pytest.mark.usefixtures("spotify_disconnected")
    def test_redirects_home_when_given_a_token(self, client):
        response = client.get(reverse('connect_spotify'), {'code': 'some_code'}, follow=True)
        assert response.redirect_chain[0][0] == 'http://testserver' + reverse('index')


    @pytest.mark.usefixtures("spotify_connected")
    def test_redirects_home_when_already_connected(self, client):
        response = client.get(reverse('connect_spotify'), follow=True)
        assert response.redirect_chain[0][0] == 'http://testserver' + reverse('index')



@pytest.mark.usefixtures("stub_get_track_mappings")
class TestDisconnectSpotify():

    def test_disconnects(self, client, spotify_connection):
        client.get(reverse('disconnect_spotify'))
        assert spotify_connection.disconnect.call_count is 1


    def test_redirects_home(self, client):
        response = client.get(reverse('disconnect_spotify'), follow=True)
        assert response.redirect_chain[0][0] == 'http://testserver' + reverse('index')
