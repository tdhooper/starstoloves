import pytest

from .. import spotify_connection_repository


pytestmark = pytest.mark.django_db



@pytest.fixture
def SpotifyConnectionHelper(create_patch):
    return create_patch('starstoloves.lib.connection.spotify_connection_repository.SpotifyConnectionHelper')



class TestSave():

    def test_persists_user_uri(self, user):
        connection = spotify_connection_repository.from_user(user)
        connection.token = 'some_token'
        spotify_connection_repository.save(connection)

        connection = spotify_connection_repository.from_user(user)
        assert connection.token == 'some_token'
