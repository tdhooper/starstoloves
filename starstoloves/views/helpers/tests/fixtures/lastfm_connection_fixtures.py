from unittest.mock import MagicMock

import pytest

from lastfm import lfm

from starstoloves.models import LastfmConnection
from starstoloves.views.helpers.lastfm_connection import LastfmConnectionHelper

from .common_connection_fixtures import CommonConnectionFixtures


class LastfmConnectionFixtures(CommonConnectionFixtures):

    connection_name = 'lastfm_connection'
    connection_class = LastfmConnection

    def __init__(self):
        super().__init__()
        self.app = MagicMock(spec=lfm.App).return_value

    @property
    def connection_without_user(self):
        return LastfmConnectionHelper(None, self.app)

    @property
    def connection_with_user(self):
        return LastfmConnectionHelper(self.user, self.app)

    @property
    def fetch_connection(self):
        return LastfmConnectionHelper(self.fetch_user, self.app)

    def successful_connection(self):
        def get_session(token):
            if (token == 'some_token'):
                return {'name': 'some_username'}
        self.app.auth.get_session.side_effect = get_session
        self.connection_with_user.connect('some_token')
