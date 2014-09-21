from unittest.mock import MagicMock, patch

import pytest

from lastfm import lfm

from starstoloves.models import LastfmConnection
from starstoloves.lib.connection.lastfm_connection import LastfmConnectionHelper

from .common_connection_fixtures import CommonConnectionFixtures
from ... import lastfm_connection_repository


class LastfmConnectionFixtures(CommonConnectionFixtures):

    connection_name = 'lastfm_connection'
    connection_class = LastfmConnection

    def __init__(self):
        super().__init__()
        self.app_patcher = patch('starstoloves.lib.connection.lastfm_connection_repository.lastfm_app')
        self.app = self.app_patcher.start()

    def finalizer(self):
        self.app_patcher.stop()
        super().finalizer()

    @property
    def connection(self):
        return lastfm_connection_repository.from_user(self.user)

    @property
    def fetch_connection(self):
        def fetch():
            return lastfm_connection_repository.from_user(self.user)
        return fetch

    def successful_connection(self):
        def get_session(token):
            if (token == 'some_token'):
                return {'name': 'some_username'}
        self.app.auth.get_session.side_effect = get_session
        self.connection.connect('some_token')

    def failed_connection(self):
        def get_session(token):
            if (token == 'some_token'):
                raise Exception()
        self.app.auth.get_session.side_effect = get_session
        self.connection.connect('some_token')
