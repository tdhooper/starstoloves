from unittest.mock import patch, call, MagicMock

import pytest

from ..result import LastfmResultParser

@pytest.fixture
def parser():
    Parser = MagicMock(spec=LastfmResultParser)
    return Parser()
