from unittest.mock import MagicMock

import pytest

from spotify import Session, Track, Playlist, PlaylistTrack, Artist


playlist_response = {
  'items': [
    {
      'added_at': '1970-01-02T11:17:36Z',
      'track': {
        'name': 'some_track',
        'artists': [
          {
            'name': 'some_artist',
          },
        ],
      },
    },
    {
      'added_at': '1970-01-10T04:10:12Z',
      'track': {
        'name': 'another_track',
        'artists': [
          {
            'name': 'another_artist',
          },
        ],
      },
    },
  ],
}

playlist_response_2 = {
  'items': [
    {
      'added_at': '2010-05-14T02:51:12Z',
      'track': {
        'name': 'other_track',
        'artists': [
          {
            'name': 'other_artist',
          },
        ],
      },
    },
  ],
}


@pytest.fixture
def Spotify_patch(create_patch):
    return create_patch('starstoloves.lib.user.spotify_user.Spotify')


@pytest.fixture
def spotify_api(Spotify_patch):
    instance = Spotify_patch.return_value
    instance.next.return_value = None
    return instance


@pytest.fixture
def spotify_user_with_starred(spotify_api):
    spotify_api.user_playlist.return_value = playlist_response


@pytest.fixture
def spotify_user_with_multiple_starred_pages(spotify_api, spotify_user_with_starred):
    def next(data):
        if data == playlist_response:
            return playlist_response_2
    spotify_api.next.side_effect = next
