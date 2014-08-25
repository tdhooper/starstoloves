from unittest.mock import patch

import pytest

from starstoloves.models import User


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
def user(request):
    user = User(session_key='some_key')
    user.save()
    def fin():
        user.delete()
    request.addfinalizer(fin)
    return user

@pytest.fixture
def fetch_user():
    return User.objects.get(session_key='some_key')
