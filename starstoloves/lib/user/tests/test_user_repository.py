from datetime import datetime
from unittest.mock import MagicMock, call

import pytest

from lastfm import lfm

from starstoloves.models import User as UserModel
from starstoloves import model_repository
from starstoloves.lib.track import lastfm_playlist_track_repository
from starstoloves.lib.track.lastfm_track import LastfmPlaylistTrack
from .. import user_repository
from ..user import User


pytestmark = pytest.mark.django_db


@pytest.fixture
def patch_spotify_user(create_patch):
    create_patch('starstoloves.lib.user.user.SpotifyUser')


@pytest.fixture
def lastfm_user(create_patch):
    return create_patch('starstoloves.lib.user.user.LastfmUser').return_value


class TestFromSessionKey():

    def test_returns_user(self):
        user = user_repository.from_session_key('some_key')
        assert isinstance(user, User)

    def test_passes_session_key(self):
        user = user_repository.from_session_key('some_key')
        assert user.session_key == 'some_key'



class TestDelete():

    @pytest.mark.usefixtures("patch_spotify_user")
    def test_deletes_stored_user(self, lastfm_user):
        lastfm_user.loved_track_urls = None

        user = user_repository.from_session_key('some_key')

        lastfm_playlist_track_repository.get_or_create(
            user=user,
            url='some_url',
            track_name='some_track',
            artist_name='some_artist',
            added=datetime.fromtimestamp(123),
        )

        user_repository.delete(user)
        user = user_repository.from_session_key('some_key')
        assert user.loved_tracks() == []
