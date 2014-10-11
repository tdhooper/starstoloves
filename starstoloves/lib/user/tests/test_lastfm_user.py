from unittest.mock import MagicMock, call

import pytest

from ..lastfm_user import LastfmUser
from starstoloves.models import LastfmTrack
from starstoloves.lib.connection.lastfm_connection import LastfmConnectionHelper

pytestmark = pytest.mark.django_db

@pytest.fixture
def lastfm_connection(create_patch):
    return MagicMock(spec=LastfmConnectionHelper).return_value

@pytest.fixture
def lastfm_user(lastfm_connection):
    return LastfmUser(lastfm_connection)

@pytest.fixture
def lastfm_app(create_patch):
    return create_patch('starstoloves.lib.user.lastfm_user.lastfm_app')

@pytest.fixture
def lastfm_api_returns_tracks(request, lastfm_app):
    lastfm_app.user.get_loved_tracks.return_value = request.cls.api_response


@pytest.mark.usefixtures('lastfm_api_returns_tracks')
class TestLovedTrackUrls():

    api_response = {
        'track': [
            {'url': 'some_url'},
            {'url': 'another_url'}
        ]
    }

    def test_it_gets_loved_tracks_from_the_lastfm_api(self, lastfm_user, lastfm_app, lastfm_connection):
        lastfm_user.loved_track_urls
        assert lastfm_app.user.get_loved_tracks.call_args == call(lastfm_connection.username)

    def test_it_returns_the_track_urls(self, lastfm_user, lastfm_app):
        assert lastfm_user.loved_track_urls == ['some_url', 'another_url']
