import builtins

from unittest.mock import MagicMock, call

import pytest

from spotify import Session, Track, Playlist, PlaylistTrack, Artist

from ..spotify_user import SpotifyUser
from starstoloves.lib.connection.spotify_connection import SpotifyConnectionHelper
from starstoloves.models import User


pytestmark = pytest.mark.django_db

track_data_list = [
    {
        'track_name': 'some_track',
        'artist_name': 'some_artist',
        'date_saved': 123456,
    },{
        'track_name': 'another_track',
        'artist_name': 'another_artist',
        'date_saved': 789012,
    },
]

@pytest.fixture
def user(request):
    user = User(session_key='some_key')
    user.save()
    def fin():
        user.delete()
    request.addfinalizer(fin)
    return user

@pytest.fixture
def fetch_user():
    return User.objects.get(session_key='some_key')

@pytest.fixture
def spotify_session():
    session = MagicMock(Session)
    builtins.spotify_session = session
    return session

@pytest.fixture
def spotify_connection(create_patch):
    patch = create_patch('starstoloves.lib.user.spotify_user.SpotifyConnectionHelper')
    return patch.return_value

@pytest.fixture
def spotify_user(user):
    return SpotifyUser(user)

@pytest.fixture
def playlist_tracks():
    tracks = []

    for track_data in track_data_list:

        artist = MagicMock(Artist)
        artist.load.return_value.name = track_data['artist_name']

        track = MagicMock(Track)
        track.load.return_value.name = track_data['track_name']
        track.load.return_value.artists = [artist]

        playlist_track = MagicMock(PlaylistTrack)
        playlist_track.create_time = track_data['date_saved']
        playlist_track.track = track

        tracks.append(playlist_track)

    return tracks

@pytest.fixture
def playlist(playlist_tracks):
    playlist = MagicMock(Playlist)
    playlist.load.return_value.tracks_with_metadata = playlist_tracks
    return playlist

@pytest.fixture
def spotify_user_with_starred(spotify_session, playlist):
    spotify_session.get_user.return_value.load.return_value.starred = playlist


@pytest.mark.usefixtures("spotify_user_with_starred", "spotify_session")
class TestStarredTracks:

    def test_starred_tracks_loads_the_user(self, spotify_user, spotify_session, spotify_connection):
        spotify_user.starred_tracks
        assert spotify_session.get_user.call_args == call(spotify_connection.get_user_uri.return_value)
        assert spotify_session.get_user.return_value.load.call_count is 1

    @pytest.mark.usefixtures("spotify_user_with_starred")
    def test_starred_tracks_loads_the_users_starred_tracks(self, spotify_user, playlist):
        spotify_user.starred_tracks
        assert playlist.load.call_count is 1

    def test_starred_tracks_returns_the_users_starred_tracks(self, spotify_user):
        assert spotify_user.starred_tracks == track_data_list

    def test_starred_tracks_stores_the_tracks(self, spotify_user, fetch_user):
        spotify_user.starred_tracks
        track_models = fetch_user.starred_tracks.all()

        assert len(track_models) is 2

        assert track_models[0].track_name   == track_data_list[0]['track_name']
        assert track_models[0].artist_name  == track_data_list[0]['artist_name']

        assert track_models[1].track_name   == track_data_list[1]['track_name']
        assert track_models[1].artist_name  == track_data_list[1]['artist_name']

    def test_starred_tracks_only_creates_one_entry_for_each_track(self, spotify_user, fetch_user):
        spotify_user.starred_tracks
        spotify_user.starred_tracks
        track_models = fetch_user.starred_tracks.all()
        assert len(track_models) is 2

