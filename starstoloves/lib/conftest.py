from unittest.mock import patch

import pytest

@pytest.fixture
def create_patch(request):
    def create_patch(module):
        patcher = patch(module)
        def fin():
            patcher.stop()
        request.addfinalizer(fin)
        return patcher.start()
    return create_patch