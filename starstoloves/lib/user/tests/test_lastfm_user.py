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
    app = create_patch('starstoloves.lib.user.lastfm_user.lastfm_app')
    app.user.get_loved_tracks.return_value = {}
    return app


@pytest.fixture
def loved_api_response():
    return {
        'track': [
            {
                'name': 'some_track',
                'artist': {
                    'name': 'some_artist',
                },
                'url': 'some_url',
                'date': {
                    'uts': '123',
                },
            },{
                'name': 'another_track',
                'artist': {
                    'name': 'another_artist',
                },
                'url': 'another_url',
                'date': {
                    'uts': '345',
                },
            },
        ]
    }


@pytest.fixture
def lastfm_api_returns_tracks(request, lastfm_app, loved_api_response):
    lastfm_app.user.get_loved_tracks.return_value = loved_api_response


def test_it_sets_the_session_key_on_the_api(lastfm_connection, lastfm_app):
    session_key_property = PropertyMock()
    type(lastfm_app).session_key = session_key_property

    LastfmUser(lastfm_connection)
    assert session_key_property.call_args == call(lastfm_connection.session_key)



@pytest.mark.usefixtures('lastfm_api_returns_tracks')
class TestLovedTracks():

    def test_it_gets_loved_tracks_from_the_lastfm_api(self, lastfm_user, lastfm_app, lastfm_connection):
        lastfm_user.loved_tracks
        assert lastfm_app.user.get_loved_tracks.call_args == call(lastfm_connection.username)


    def test_it_returns_the_track_urls_and_dates(self, lastfm_user, lastfm_app):
        assert lastfm_user.loved_tracks == [
            {
                'track_name': 'some_track',
                'artist_name': 'some_artist',
                'url': 'some_url',
                'added': 123,
            },{
                'track_name': 'another_track',
                'artist_name': 'another_artist',
                'url': 'another_url',
                'added': 345,
            },
        ]


    def test_it_returns_none_when_not_connected(self, lastfm_user, lastfm_app, lastfm_connection):
        lastfm_connection.is_connected = False
        assert lastfm_user.loved_tracks == None
        assert lastfm_app.user.get_loved_tracks.call_count is 0



class TestLovedTracksEmpty():

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


class TestLoveTracks():

    def test_it_proxies_to_api(self, lastfm_user, lastfm_app):
        lastfm_user.love_tracks([
            {
                'track_name': 'some_track',
                'artist_name': 'some_artist',
                'timestamp': 123,
            },{
                'track_name': 'another_track',
                'artist_name': 'another_artist',
                'timestamp': 456,
            },
        ])
        assert lastfm_app.request.call_args_list == [
            call(
                'track',
                'love',
                {
                    'track': 'some_track',
                    'artist': 'some_artist',
                    'timestamp': 123,
                },
            ),
            call(
                'track',
                'love',
                {
                    'track': 'another_track',
                    'artist': 'another_artist',
                    'timestamp': 456,
                },
            )
        ]


    @pytest.mark.usefixtures('lastfm_api_returns_tracks')
    def test_it_unloves_already_loved_tracks_before_loving(self, lastfm_user, lastfm_app):

        unloved_tracks = []
        loved_tracks = [
            {
                'artist_name': track['artist_name'],
                'track_name': track['track_name'],
            }
            for track in lastfm_user.loved_tracks
        ]

        def unlove(artist, track):
            unloved_tracks.append({
                'artist_name': artist,
                'track_name': track,
            })

        def request(package, method, data):
            track = {
                'artist_name': data['artist'],
                'track_name': data['track'],
            }
            if track in loved_tracks:
                assert track in unloved_tracks
            else:
                assert track not in unloved_tracks

        lastfm_app.track.unlove.side_effect = unlove
        lastfm_app.request.side_effect = request

        lastfm_user.love_tracks([
            {
                'track_name': 'some_track',
                'artist_name': 'some_artist',
                'timestamp': 123,
            },{
                'track_name': 'another_track',
                'artist_name': 'another_artist',
                'timestamp': 456,
            },{
                'track_name': 'other_track',
                'artist_name': 'other_artist',
                'timestamp': 789,
            },
        ])


    def test_it_only_gets_loved_tracks_once(self, lastfm_user, lastfm_app):
        lastfm_user.love_tracks([
            {
                'track_name': 'some_track',
                'artist_name': 'some_artist',
                'timestamp': 123,
            },{
                'track_name': 'another_track',
                'artist_name': 'another_artist',
                'timestamp': 456,
            },
        ])
        assert lastfm_app.user.get_loved_tracks.call_count is 1
