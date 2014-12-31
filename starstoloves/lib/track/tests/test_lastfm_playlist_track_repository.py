from datetime import datetime

import pytest

from starstoloves.models import LastfmPlaylistTrack as LastfmPlaylistTrackModel
from starstoloves.models import User as UserModel
from starstoloves import model_repository
from starstoloves.lib.user import user_repository
from .. import lastfm_playlist_track_repository
from ..lastfm_track import LastfmPlaylistTrack, LastfmTrack


pytestmark = pytest.mark.django_db


@pytest.fixture
def playlist_track(user):
    return lastfm_playlist_track_repository.get_or_create(
            user=user,
            url='some_url',
            track_name='some_track',
            artist_name='some_artist',
            listeners=5,
            added=datetime.fromtimestamp(12345)
        )


@pytest.fixture
def another_playlist_track(user):
    return lastfm_playlist_track_repository.get_or_create(
            user=user,
            url='another_url',
            track_name='another_track',
            artist_name='another_artist',
            listeners=10,
            added=datetime.fromtimestamp(111)
        )


@pytest.fixture
def another_user():
    return user_repository.from_session_key('another_some_key')


@pytest.fixture
def another_user_playlist_track(another_user):
    return lastfm_playlist_track_repository.get_or_create(
            user=another_user,
            url='tother_url',
            track_name='tother_track',
            artist_name='tother_artist',
            listeners=20,
            added=datetime.fromtimestamp(222)
        )


class TestGetOrCreate:

    def test_returns_a_lastfm_playlist_track(self, playlist_track):
        assert isinstance(playlist_track, LastfmPlaylistTrack)

    def test_assigns_parameters_as_properties(self, playlist_track, user):
        assert playlist_track.user == user
        assert playlist_track.url == 'some_url'
        assert playlist_track.track_name == 'some_track'
        assert playlist_track.artist_name == 'some_artist'
        assert playlist_track.listeners == 5
        assert playlist_track.added.timestamp() == 12345

    def test_stores_in_db(self, playlist_track, user):
        user_model = model_repository.from_user(user)
        track_model = model_repository.from_lastfm_track(playlist_track)
        assert LastfmPlaylistTrackModel.objects.filter(
            user=user_model,
            track=track_model,
            added=datetime.fromtimestamp(12345)
        ).count() is 1


class TestForUser:

    def test_returns_all_tracks_associated_with_a_user(
        self,
        user,
        another_user,
        playlist_track,
        another_playlist_track,
        another_user_playlist_track
    ):
        user_tracks = lastfm_playlist_track_repository.for_user(user)
        assert len(user_tracks) is 2
        assert isinstance(user_tracks[0], LastfmPlaylistTrack)
        assert user_tracks[0].user == user
        assert user_tracks[0].url == 'some_url'
        assert user_tracks[0].track_name == 'some_track'
        assert user_tracks[0].artist_name == 'some_artist'
        assert user_tracks[0].added.timestamp() == 12345
        assert user_tracks[0].listeners == 5
        assert isinstance(user_tracks[1], LastfmPlaylistTrack)
        assert user_tracks[1].user == user
        assert user_tracks[1].url == 'another_url'
        assert user_tracks[1].track_name == 'another_track'
        assert user_tracks[1].artist_name == 'another_artist'
        assert user_tracks[1].added.timestamp() == 111
        assert user_tracks[1].listeners == 10

        another_user_tracks = lastfm_playlist_track_repository.for_user(another_user)
        assert len(another_user_tracks) is 1
        assert isinstance(another_user_tracks[0], LastfmPlaylistTrack)
        assert another_user_tracks[0].user == another_user
        assert another_user_tracks[0].url == 'tother_url'
        assert another_user_tracks[0].track_name == 'tother_track'
        assert another_user_tracks[0].artist_name == 'tother_artist'
        assert another_user_tracks[0].added.timestamp() == 222
        assert another_user_tracks[0].listeners == 20
