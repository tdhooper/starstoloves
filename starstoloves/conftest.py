from unittest.mock import patch

import pytest

from starstoloves.models import User
from starstoloves.lib.user import user_repository


@pytest.fixture
def create_patch(request):
    def create_patch(*args, **kwargs):
        patcher = patch(*args, **kwargs)
        def fin():
            patcher.stop()
        request.addfinalizer(fin)
        return patcher.start()
    return create_patch

@pytest.fixture
def user():
    return user_repository.from_session_key('some_key')

@pytest.fixture
def fetch_user():
    def fetch():
        return user_repository.from_session_key('some_key')
    return fetch
