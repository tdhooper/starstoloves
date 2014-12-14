import pytest

from .. import lastfm_connection_repository


pytestmark = pytest.mark.django_db


class TestSave():

    def test_persists_session_key(self, user):
        connection = lastfm_connection_repository.from_user(user)
        connection.session_key = 'some_other_key'
        lastfm_connection_repository.save(connection)

        connection = lastfm_connection_repository.from_user(user)
        assert connection.session_key == 'some_other_key'
