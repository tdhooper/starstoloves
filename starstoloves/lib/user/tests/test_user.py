import pytest

from unittest.mock import MagicMock, call, PropertyMock

from starstoloves.lib.track.spotify_track import SpotifyPlaylistTrack
from starstoloves.lib.track.lastfm_track import LastfmTrack
from starstoloves.lib.user import user_repository
from ..user import User



pytestmark = pytest.mark.django_db



@pytest.fixture
def spotify_connection_repository(create_patch):
    return create_patch('starstoloves.lib.user.user.spotify_connection_repository')


@pytest.fixture
def lastfm_connection_repository(create_patch):
    return create_patch('starstoloves.lib.user.user.lastfm_connection_repository')


@pytest.fixture
def SpotifyUser(create_patch):
    return create_patch('starstoloves.lib.user.user.SpotifyUser')


@pytest.fixture
def LastfmUser(create_patch):
    return create_patch('starstoloves.lib.user.user.LastfmUser')


@pytest.fixture
def spotify_user(SpotifyUser):
    return SpotifyUser.return_value


@pytest.fixture
def loved_track_urls_property():
    return PropertyMock(return_value=[
        'some_url_a',
        'some_url_b',
    ])


@pytest.fixture
def lastfm_user(LastfmUser, loved_track_urls_property):
    instance = LastfmUser.return_value
    type(instance).loved_track_urls = loved_track_urls_property
    return instance



class TestUser:

    def test_returns_values_it_was_created_with(self):
        user = User('some_key', 'some_loved_tracks')
        assert user.session_key == 'some_key'
        assert user.loved_tracks == 'some_loved_tracks'



class TestUserStarredTracks:

    starred_tracks = [
            {
                'track_name': 'some_track',
                'artist_name': 'some_artist',
                'date_saved': 123,
            }
        ]


    def test_spotify_user_is_created_with_spotify_connection(self, user, SpotifyUser, spotify_connection_repository):
        spotify_user = user.spotify_user
        assert spotify_connection_repository.from_user.call_args == call(user)
        assert SpotifyUser.call_args == call(spotify_connection_repository.from_user.return_value)
        assert spotify_user is SpotifyUser.return_value


    def test_returns_SpotifyPlaylistTracks(self, user, spotify_user):
        spotify_user.starred_tracks = self.starred_tracks
        assert isinstance(user.starred_tracks[0], SpotifyPlaylistTrack)


    def test_uses_starred_tracks_data_from_spotify_user(self, user, spotify_user):
        spotify_user.starred_tracks = self.starred_tracks
        assert user.starred_tracks[0].user == user
        assert user.starred_tracks[0].track_name == 'some_track'
        assert user.starred_tracks[0].artist_name == 'some_artist'
        assert user.starred_tracks[0].added.timestamp() == 123


    def test_stores_starred_tracks(self, user, spotify_user):
        starred_tracks_property = PropertyMock(return_value=self.starred_tracks)
        type(spotify_user).starred_tracks = starred_tracks_property

        user.starred_tracks
        new_user = user_repository.from_session_key('some_key')
        starred_tracks = new_user.starred_tracks

        assert starred_tracks[0].user == new_user
        assert starred_tracks[0].track_name == 'some_track'
        assert starred_tracks[0].artist_name == 'some_artist'
        assert starred_tracks[0].added.timestamp() == 123

        assert starred_tracks_property.call_count is 1



class TestUserLoveTracks:

    def test_lastfm_user_is_created_with_lastfm_connection(self, user, LastfmUser, lastfm_connection_repository):
        lastfm_user = user.lastfm_user
        assert lastfm_connection_repository.from_user.call_args == call(user)
        assert LastfmUser.call_args == call(lastfm_connection_repository.from_user.return_value)
        assert lastfm_user is LastfmUser.return_value


    def test_proxies_to_lastfm_user(self, user, lastfm_user):
        tracks = [
            LastfmTrack('some_url_a', 'some_track_a', 'some_artist_a'),
            LastfmTrack('some_url_b', 'some_track_b', 'some_artist_b'),
        ]
        user.love_tracks(tracks)
        assert lastfm_user.love_track.call_args_list == [
            call(track_name='some_track_a', artist_name='some_artist_a'),
            call(track_name='some_track_b', artist_name='some_artist_b'),
        ]



class TestUserLovedTracks:

    def test_returns_LastfmTracks_from_lastfm_user_loved_track_urls(self, user, lastfm_user):
        tracks = user.loved_tracks

        assert isinstance(tracks[0], LastfmTrack)
        assert tracks[0].url == 'some_url_a'

        assert isinstance(tracks[1], LastfmTrack)
        assert tracks[1].url == 'some_url_b'


    def test_does_not_regenerate_LastfmTracks_each_time_called(self, user, lastfm_user, loved_track_urls_property):
        tracks = user.loved_tracks
        tracks_again = user.loved_tracks

        assert tracks is tracks_again
        assert loved_track_urls_property.call_count is 1


    def test_persists_result(self, user, lastfm_user, loved_track_urls_property):
        tracks = user.loved_tracks

        user_again = user_repository.from_session_key(user.session_key)
        tracks_again = user_again.loved_tracks

        assert tracks == tracks_again
        assert loved_track_urls_property.call_count is 1
