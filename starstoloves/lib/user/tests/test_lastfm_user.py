from unittest.mock import MagicMock, call, PropertyMock

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



def test_it_sets_the_session_key_on_the_api(lastfm_connection, lastfm_app):
    session_key_property = PropertyMock()
    type(lastfm_app).session_key = session_key_property

    LastfmUser(lastfm_connection)
    assert session_key_property.call_args == call(lastfm_connection.session_key)



@pytest.mark.usefixtures('lastfm_api_returns_tracks')
class TestLovedTracks():

    api_response = {
        'track': [
            {
                'url': 'some_url',
                'date': {
                    'uts': '123',
                },
            },{
                'url': 'another_url',
                'date': {
                    'uts': '345',
                },
            },
        ]
    }

    def test_it_gets_loved_tracks_from_the_lastfm_api(self, lastfm_user, lastfm_app, lastfm_connection):
        lastfm_user.loved_tracks
        assert lastfm_app.user.get_loved_tracks.call_args == call(lastfm_connection.username)


    def test_it_returns_the_track_urls_and_dates(self, lastfm_user, lastfm_app):
        assert lastfm_user.loved_tracks == [
            {
                'url': 'some_url',
                'added': 123,
            },{
                'url': 'another_url',
                'added': 345,
            },
        ]


    def test_it_returns_none_when_not_connected(self, lastfm_user, lastfm_app, lastfm_connection):
        lastfm_connection.is_connected = False
        assert lastfm_user.loved_tracks == None
        assert lastfm_app.user.get_loved_tracks.call_count is 0



@pytest.mark.usefixtures('lastfm_api_returns_tracks')
class TestLovedTracksEmpty():

    api_response = {}

    def test_it_returns_none(self, lastfm_user, lastfm_app):
        assert lastfm_user.loved_tracks == None



class TestLoveTrack():

    def test_it_proxies_to_api(self, lastfm_user, lastfm_app):
        lastfm_user.love_track(track_name='some_track', artist_name='some_artist', timestamp=123)
        assert lastfm_app.request.call_args == call(
            'track',
            'love',
            {
                'track': 'some_track',
                'artist': 'some_artist',
                'timestamp': 123,
            },
        )
