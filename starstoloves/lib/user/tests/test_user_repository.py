from unittest.mock import MagicMock, call

import pytest

from lastfm import lfm

from starstoloves.models import SpotifyTrack, LastfmTrack
from .. import user_repository
from ..user import User


pytestmark = pytest.mark.django_db


@pytest.fixture
def spotify_track_models():
     return [
        SpotifyTrack.objects.create(
            track_name=track['track_name'],
            artist_name=track['artist_name'],
        )
        for track in [{
            'track_name': 'some_track',
            'artist_name': 'some_artist',
        },{
            'track_name': 'another_track',
            'artist_name': 'another_artist',
        }]
    ]

@pytest.fixture
def lastfm_track_models():
     return [
        LastfmTrack.objects.create(
            track_name=track['track_name'],
            artist_name=track['artist_name'],
            url=track['url'],
        )
        for track in [{
            'track_name': 'some_track',
            'artist_name': 'some_artist',
            'url': 'some_url',
        },{
            'track_name': 'another_track',
            'artist_name': 'another_artist',
            'url': 'another_url',
        }]
    ]


class TestFromSessionKey():

    def test_returns_user(self):
        user = user_repository.from_session_key('some_key')
        assert isinstance(user, User)

    def test_passes_session_key(self):
        user = user_repository.from_session_key('some_key')
        assert user.session_key == 'some_key'


class TestSave():

    def test_persists_starred_tracks(self, spotify_track_models):
        user = user_repository.from_session_key('some_key')
        user.starred_tracks = spotify_track_models
        user_repository.save(user)

        user = user_repository.from_session_key('some_key')
        tracks = user.starred_tracks.values()
        assert tracks[0]['track_name'] == 'some_track';
        assert tracks[0]['artist_name'] == 'some_artist';
        assert tracks[1]['track_name'] == 'another_track';
        assert tracks[1]['artist_name'] == 'another_artist';

    def test_persists_loved_tracks(self, lastfm_track_models):
        user = user_repository.from_session_key('some_key')
        user.loved_tracks = lastfm_track_models
        user_repository.save(user)

        user = user_repository.from_session_key('some_key')
        tracks = user.loved_tracks.values()
        assert tracks[0]['track_name'] == 'some_track';
        assert tracks[0]['artist_name'] == 'some_artist';
        assert tracks[0]['url'] == 'some_url';
        assert tracks[1]['track_name'] == 'another_track';
        assert tracks[1]['artist_name'] == 'another_artist';
        assert tracks[1]['url'] == 'another_url';


class TestDelete():

    def test_deletes_stored_user(self, spotify_track_models, lastfm_track_models):
        user = user_repository.from_session_key('some_key')
        user.starred_tracks = spotify_track_models
        user.loved_tracks = lastfm_track_models
        user_repository.save(user)

        user_repository.delete(user)
        user = user_repository.from_session_key('some_key')
        assert user.starred_tracks is None
        assert user.loved_tracks is None
