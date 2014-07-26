from unittest.mock import patch, call, MagicMock

import pytest

from ..result import LastfmResultParser


def create_patch(request, module):
    patcher = patch(module)
    def fin():
        patcher.stop()
    request.addfinalizer(fin)
    return patcher.start()

@pytest.fixture
def parser():
    Parser = MagicMock(spec=LastfmResultParser)
    return Parser()
