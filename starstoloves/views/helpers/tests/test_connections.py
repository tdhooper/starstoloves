import pytest

from starstoloves.views.helpers.connection import MissingUserError

from .fixtures.connection_fixtures import *


pytestmark = pytest.mark.django_db

def test_state_defaults_to_disconnected(connection):
    assert connection.get_connection_state() == connection.DISCONNECTED

def test_username_defaults_to_none(connection):
    assert connection.get_username() is None

def test_disconnect_is_a_noop(connection):
    connection.disconnect()

def test_connect_throws(connection_without_user):
    with pytest.raises(MissingUserError):
        connection_without_user.connect('some_token')

