import pytest

from starstoloves.models import User
from starstoloves.lib.user import repository


class CommonConnectionFixtures():

    def __init__(self):
        self.user = repository.from_session_key('some_key')

    def finalizer(self):
        repository.delete(self.user)

    @property
    def fetch_user(self):
        return repository.from_session_key('some_key')

    @property
    def fetch_user_model(self):
        return User.objects.get(session_key='some_key')

    def disconnected_connection(self):
        self.connection_with_user.disconnect()
