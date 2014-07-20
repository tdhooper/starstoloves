from unittest.mock import MagicMock

import pytest

from .fixtures.connection_fixtures import *


pytestmark = pytest.mark.django_db

@pytest.fixture
def app(fixtures):
    return fixtures.app


@pytest.mark.lastfm_only
def test_get_auth_url_proxies_to_app(connection, app):
    def get_url(callback_url):
        if (callback_url == 'some_callback'):
            return 'some_auth_url'
    app.auth.get_url.side_effect = get_url
    auth_url = connection.get_auth_url('some_callback')
    assert auth_url == 'some_auth_url'

