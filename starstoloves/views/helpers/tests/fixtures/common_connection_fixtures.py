import pytest

from starstoloves.models import User


class CommonConnectionFixtures():

    def __init__(self):
        self.user = User(session_key='some_key')
        self.user.save()

    def finalizer(self):
        self.user.delete()
