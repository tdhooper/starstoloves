import pytest

from .. import spotify_connection_repository


pytestmark = pytest.mark.django_db


class TestSave():

    def test_persists_user_uri(self, user):
        connection = spotify_connection_repository.from_user(user)
        connection.user_uri = 'some_uri'
        spotify_connection_repository.save(connection)

        connection = spotify_connection_repository.from_user(user)
        assert connection.user_uri == 'some_uri'
