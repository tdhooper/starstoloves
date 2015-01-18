import pytest

from .. import spotify_connection_repository


pytestmark = pytest.mark.django_db


@pytest.fixture
def SpotifyOAuth(create_patch):
    return create_patch('starstoloves.lib.connection.spotify_connection_repository.SpotifyOAuth', autospec=True)


@pytest.fixture
def SpotifyConnectionHelper(create_patch):
    return create_patch('starstoloves.lib.connection.spotify_connection_repository.SpotifyConnectionHelper')



class TestFromUser():

    def test_creates_spotipy_auth_instance(self, user, SpotifyConnectionHelper, SpotifyOAuth):
        connection = spotify_connection_repository.from_user(user, 'some_callback_url')
        assert SpotifyOAuth.call_args[1]['redirect_uri'] == 'some_callback_url'
        assert SpotifyConnectionHelper.call_args[0][1] is SpotifyOAuth.return_value


class TestSave():

    def test_persists_user_uri(self, user):
        connection = spotify_connection_repository.from_user(user, 'some_callback_url')
        connection.token = 'some_token'
        spotify_connection_repository.save(connection)

        connection = spotify_connection_repository.from_user(user, 'some_callback_url')
        assert connection.token == 'some_token'
