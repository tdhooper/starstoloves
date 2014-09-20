from unittest.mock import call

import pytest

from ..lastfm_user import LastfmUser
from starstoloves.models import LastfmTrack


pytestmark = pytest.mark.django_db

@pytest.fixture
def LastfmConnectionHelper_patch(create_patch):
    return create_patch('starstoloves.lib.user.lastfm_user.LastfmConnectionHelper')

@pytest.fixture
def lastfm_user(user):
    return LastfmUser(user)

@pytest.fixture
def lastfm_app(create_patch):
    return create_patch('starstoloves.lib.user.lastfm_user.lastfm_app')

@pytest.fixture
def lastfm_api_returns_tracks(request, lastfm_app):
    lastfm_app.user.get_loved_tracks.return_value = request.cls.api_response

def test_connection_returns_the_lastfm_connection(lastfm_user, user, lastfm_app, LastfmConnectionHelper_patch):
    assert lastfm_user.connection is LastfmConnectionHelper_patch.return_value
    assert LastfmConnectionHelper_patch.call_args == call(user, lastfm_app)


@pytest.mark.usefixtures('lastfm_api_returns_tracks')
class TestLovedTrackUrls():

    api_response = {
        'track': [
            {'url': 'some_url'},
            {'url': 'another_url'}
        ]
    }

    @pytest.mark.usefixtures('LastfmConnectionHelper_patch')
    def test_it_gets_loved_tracks_from_the_lastfm_api(self, lastfm_user, lastfm_app):
        lastfm_user.loved_track_urls
        assert lastfm_app.user.get_loved_tracks.call_args == call(lastfm_user.connection.get_username.return_value)

    def test_it_returns_the_track_urls(self, lastfm_user, lastfm_app):
        assert lastfm_user.loved_track_urls == ['some_url', 'another_url']

    def test_the_urls_are_stored_on_the_user_model(self, lastfm_user, fetch_user):
        lastfm_user.loved_track_urls
        stored_urls = [track.url for track in fetch_user().loved_tracks]
        assert stored_urls == ['some_url', 'another_url']

    def test_it_does_not_call_the_api_again_when_called_twice(self, lastfm_user, lastfm_app):
        lastfm_user.loved_track_urls
        lastfm_user.loved_track_urls
        assert lastfm_app.user.get_loved_tracks.call_count is 1
