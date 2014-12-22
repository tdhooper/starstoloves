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
class TestConnectSpotify():

    @pytest.mark.usefixtures("spotify_disconnected")
    def test_connects_when_given_a_username(self, client, spotify_connection):
        client.post(reverse('index'), {'username': 'some_username'})
        assert spotify_connection.connect.call_args == call('some_username')


    @pytest.mark.usefixtures("spotify_disconnected")
    def test_stops_double_posts_when_connection_succeeds(self, client, spotify_connection):
        response = client.post(reverse('index'), {'username': 'some_username'}, follow=True)
        assert response.redirect_chain[0][0] == 'http://testserver' + reverse('index')


    @pytest.mark.usefixtures("spotify_disconnected")
    def test_displays_error_when_connection_fails(self, client, spotify_connection):
        def connect(username):
            spotify_connection.state = spotify_connection.FAILED
        spotify_connection.connect.side_effect = connect

        response = client.post(reverse('index'), {'username': 'some_username'}, follow=True)
        assert response.context['spForm'].errors['username'][0] == 'User not found'


class TestDisconnectSpotify():

    def test_disconnects(self, client, spotify_connection, create_patch):
        create_patch('starstoloves.views.main.get_track_mappings')
        client.get(reverse('disconnect_spotify'))
        assert spotify_connection.disconnect.call_count is 1


    def test_redirects_home(self, client):
        response = client.get(reverse('disconnect_spotify'), follow=True)
        assert response.redirect_chain[0][0] == 'http://testserver' + reverse('index')
