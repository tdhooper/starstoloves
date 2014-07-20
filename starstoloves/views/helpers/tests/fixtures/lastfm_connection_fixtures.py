from unittest.mock import MagicMock

import pytest

from lastfm import lfm

from starstoloves.views.helpers.lastfm_connection import LastfmConnectionHelper

from .common_connection_fixtures import CommonConnectionFixtures


class LastfmConnectionFixtures(CommonConnectionFixtures):

    def __init__(self):
        super().__init__()
        self.app = MagicMock(spec=lfm.App).return_value

    @property
    def connection_without_user(self):
        return LastfmConnectionHelper(None, self.app)

    @property
    def connection_with_user(self):
        return LastfmConnectionHelper(self.user, self.app)
