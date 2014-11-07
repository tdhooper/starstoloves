from unittest.mock import MagicMock

import pytest

from spotify import Session, Track, Playlist, PlaylistTrack, Artist


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
def spotify_session(create_patch):
    return create_patch('starstoloves.lib.user.spotify_user.spotify_session')


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
