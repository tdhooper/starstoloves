from datetime import datetime

import pytest

from starstoloves.models import SpotifyPlaylistTrack as SpotifyPlaylistTrackModel
from starstoloves.models import User as UserModel
from starstoloves import model_repository
from starstoloves.lib.user import user_repository
from .. import spotify_playlist_track_repository
from ..spotify_track import SpotifyPlaylistTrack, SpotifyTrack


pytestmark = pytest.mark.django_db


@pytest.fixture
def playlist_track(user):
    return spotify_playlist_track_repository.get_or_create(
            user=user,
            track_name='some_track',
            artist_name='some_artist',
            added=datetime.fromtimestamp(12345)
        )


@pytest.fixture
def another_playlist_track(user):
    return spotify_playlist_track_repository.get_or_create(
            user=user,
            track_name='another_track',
            artist_name='another_artist',
            added=datetime.fromtimestamp(111)
        )


@pytest.fixture
def another_user():
    return user_repository.from_session_key('another_some_key')


@pytest.fixture
def another_user_playlist_track(another_user):
    return spotify_playlist_track_repository.get_or_create(
            user=another_user,
            track_name='tother_track',
            artist_name='tother_artist',
            added=datetime.fromtimestamp(222)
        )


class TestGetOrCreate:

    def test_returns_a_spotify_playlist_track(self, playlist_track):
        assert isinstance(playlist_track, SpotifyPlaylistTrack)

    def test_assigns_parameters_as_properties(self, playlist_track, user):
        assert playlist_track.user == user
        assert playlist_track.track_name == 'some_track'
        assert playlist_track.artist_name == 'some_artist'
        assert playlist_track.added.timestamp() == 12345

    def test_stores_in_db(self, playlist_track, user):
        user_model = model_repository.from_user(user)
        track_model = model_repository.from_spotify_track(playlist_track)
        assert SpotifyPlaylistTrackModel.objects.filter(
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
        user_tracks = spotify_playlist_track_repository.for_user(user)
        assert len(user_tracks) is 2
        assert isinstance(user_tracks[0], SpotifyPlaylistTrack)
        assert user_tracks[0].user == user
        assert user_tracks[0].track_name == 'some_track'
        assert user_tracks[0].artist_name == 'some_artist'
        assert user_tracks[0].added.timestamp() == 12345
        assert isinstance(user_tracks[1], SpotifyPlaylistTrack)
        assert user_tracks[1].user == user
        assert user_tracks[1].track_name == 'another_track'
        assert user_tracks[1].artist_name == 'another_artist'
        assert user_tracks[1].added.timestamp() == 111

        another_user_tracks = spotify_playlist_track_repository.for_user(another_user)
        assert len(another_user_tracks) is 1
        assert isinstance(another_user_tracks[0], SpotifyPlaylistTrack)
        assert another_user_tracks[0].user == another_user
        assert another_user_tracks[0].track_name == 'tother_track'
        assert another_user_tracks[0].artist_name == 'tother_artist'
        assert another_user_tracks[0].added.timestamp() == 222



class TestClearUser:

    def test_removes_loved_tracks_from_user(
        self,
        user,
        playlist_track,
        another_playlist_track,
    ):
        assert len(spotify_playlist_track_repository.for_user(user)) is 2

        spotify_playlist_track_repository.clear_user(user)
        assert spotify_playlist_track_repository.for_user(user) == []


    def test_copes_with_no_loved_tracks(self, user):
        assert spotify_playlist_track_repository.for_user(user) == []
        spotify_playlist_track_repository.clear_user(user)
