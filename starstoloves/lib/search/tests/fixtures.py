import pytest

from unittest.mock import MagicMock

from celery.result import AsyncResult


@pytest.fixture
def async_result():
    result = MagicMock(spec=AsyncResult).return_value
    result.id = 'some_id'
    return result


