import pytest

from unittest.mock import MagicMock

from celery.result import AsyncResult


@pytest.fixture
def async_result():
    result = MagicMock(spec=AsyncResult).return_value
    result.id = 'some_id'
    return result


@pytest.fixture
def search_lastfm(create_patch, async_result):
    return create_patch('starstoloves.lib.search.query.search_lastfm')


@pytest.fixture
def lastfm_app(create_patch):
    return create_patch('starstoloves.lib.search.strategies.lastfm_app')