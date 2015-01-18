import builtins

import pytest

from .. import lastfm_connection_repository, spotify_connection_repository
from ..lastfm_connection import LastfmConnectionHelper
from ..spotify_connection import SpotifyConnectionHelper


pytestmark = pytest.mark.django_db


@pytest.fixture(params=[True, False])
def connection_fixtures(request):
    if request.param:
        return {
            'repository': lastfm_connection_repository,
            'class': LastfmConnectionHelper,
            'from_user': lambda user: lastfm_connection_repository.from_user(user)
        }
    return {
            'repository': spotify_connection_repository,
            'class': SpotifyConnectionHelper,
            'from_user': lambda user: spotify_connection_repository.from_user(user, 'some_callback_url')
        }

@pytest.fixture
def repository(connection_fixtures):
    return connection_fixtures['repository']

@pytest.fixture
def connection_class(connection_fixtures):
    return connection_fixtures['class']

@pytest.fixture
def from_user(connection_fixtures):
    return connection_fixtures['from_user']



class TestFromUser():

    def test_returns_connection(self, user, repository, connection_class, from_user):
        connection = from_user(user)
        assert isinstance(connection, connection_class)


class TestSave():

    def test_persists_username(self, user, repository, from_user):
        connection = from_user(user)
        connection.username = 'some_username'
        repository.save(connection)

        connection = from_user(user)
        assert connection.username == 'some_username'

    def test_persists_connection_state(self, user, repository, from_user):
        connection = from_user(user)
        connection.state = connection.CONNECTED
        repository.save(connection)

        connection = from_user(user)
        assert connection.state == connection.CONNECTED


class TestDelete():

    def test_deletes_stored_connection(self, user, repository, from_user):
        connection = from_user(user)
        connection.username = 'some_username'
        connection.state = connection.CONNECTED
        repository.save(connection)

        repository.delete(connection)
        connection = from_user(user)
        assert connection.username is None
        assert connection.state is connection.DISCONNECTED
