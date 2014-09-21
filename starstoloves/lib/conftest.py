import builtins
from unittest.mock import patch

import pytest

from starstoloves.models import User
from starstoloves.lib.user import repository


builtins.spotify_session = 'spotify_api_session'

@pytest.fixture
def create_patch(request):
    def create_patch(module):
        patcher = patch(module)
        def fin():
            patcher.stop()
        request.addfinalizer(fin)
        return patcher.start()
    return create_patch

@pytest.fixture
def user():
    return repository.from_session_key('some_key')

@pytest.fixture
def fetch_user():
    def fetch():
        return repository.from_session_key('some_key')
    return fetch
