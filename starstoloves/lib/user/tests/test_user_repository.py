from unittest.mock import MagicMock, call

import pytest

from lastfm import lfm

from starstoloves.models import User as UserModel
from starstoloves import model_repository
from starstoloves.lib.track import lastfm_track_repository
from starstoloves.lib.track.lastfm_track import LastfmTrack
from .. import user_repository
from ..user import User


pytestmark = pytest.mark.django_db


@pytest.fixture
def lastfm_tracks():
     return [
        lastfm_track_repository.get_or_create(
            url=track['url'],
            track_name=track['track_name'],
            artist_name=track['artist_name'],
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


@pytest.fixture
def patch_spotify_user(create_patch):
    create_patch('starstoloves.lib.user.user.SpotifyUser')


class TestFromSessionKey():

    def test_returns_user(self):
        user = user_repository.from_session_key('some_key')
        assert isinstance(user, User)

    def test_passes_session_key(self):
        user = user_repository.from_session_key('some_key')
        assert user.session_key == 'some_key'


class TestSave():

    @pytest.mark.usefixtures("patch_spotify_user")
    def test_persists_loved_tracks(self, lastfm_tracks):
        user = user_repository.from_session_key('some_key')
        user.loved_tracks = lastfm_tracks
        user_repository.save(user)

        user = user_repository.from_session_key('some_key')
        tracks = user.loved_tracks

        assert isinstance(tracks[0], LastfmTrack)
        assert tracks[0].track_name == 'some_track'
        assert tracks[0].artist_name == 'some_artist'
        assert tracks[0].url == 'some_url'

        assert isinstance(tracks[1], LastfmTrack)
        assert tracks[1].track_name == 'another_track'
        assert tracks[1].artist_name == 'another_artist'
        assert tracks[1].url == 'another_url'


class TestDelete():

    @pytest.mark.usefixtures("patch_spotify_user")
    def test_deletes_stored_user(self, lastfm_tracks):
        user = user_repository.from_session_key('some_key')
        user.loved_tracks = lastfm_tracks
        user_repository.save(user)

        user_repository.delete(user)
        user = user_repository.from_session_key('some_key')
        assert user.loved_tracks is None
