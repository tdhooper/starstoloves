import pytest

from .lastfm_connection_fixtures import LastfmConnectionFixtures
from .spotify_connection_fixtures import SpotifyConnectionFixtures


@pytest.fixture(params=[LastfmConnectionFixtures, SpotifyConnectionFixtures])
def fixtures(request):
    if 'lastfm_only' in request.keywords and request.param is not LastfmConnectionFixtures:
        pytest.skip("Lastfm only")

    if 'spotify_only' in request.keywords and request.param is not SpotifyConnectionFixtures:
        pytest.skip("Spotify only")

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

@pytest.fixture
def fetch_user_model(fixtures):
    return fixtures.fetch_user_model

@pytest.fixture
def fetch_connection(fixtures):
    return fixtures.fetch_connection

@pytest.fixture
def connection_name(fixtures):
    return fixtures.connection_name

@pytest.fixture
def connection_class(fixtures):
    return fixtures.connection_class

@pytest.fixture
def successful_connection(fixtures):
    fixtures.successful_connection()

@pytest.fixture
def failed_connection(fixtures):
    fixtures.failed_connection()

@pytest.fixture
def disconnected_connection(fixtures):
    fixtures.disconnected_connection()
