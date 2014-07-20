import pytest

from .lastfm_connection_fixtures import LastfmConnectionFixtures
from .spotify_connection_fixtures import SpotifyConnectionFixtures


@pytest.fixture(params=[LastfmConnectionFixtures, SpotifyConnectionFixtures])
def fixtures(request):
    if 'lastfm_only' in request.keywords and request.param is not LastfmConnectionFixtures:
        pytest.skip("Lastfm only")

    fixtures = request.param()
    request.addfinalizer(fixtures.finalizer)
    return fixtures;

@pytest.fixture
def connection_without_user(fixtures):
    return fixtures.connection_without_user

@pytest.fixture
def connection_with_user(fixtures):
    return fixtures.connection_with_user

@pytest.fixture(params=[True, False])
def connection(request, connection_with_user, connection_without_user):
    if request.param:
        return connection_with_user
    else:
        return connection_without_user
