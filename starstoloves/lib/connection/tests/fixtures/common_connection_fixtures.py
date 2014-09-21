import pytest

from starstoloves.models import User
from starstoloves.lib.user import user_repository


class CommonConnectionFixtures(object):

    def __init__(self):
        self.user = user_repository.from_session_key('some_key')

    def finalizer(self):
        user_repository.delete(self.user)

    @property
    def fetch_user(self):
        return user_repository.from_session_key('some_key')

    @property
    def fetch_user_model(self):
        return User.objects.get(session_key='some_key')

    def disconnected_connection(self):
        self.connection.disconnect()
