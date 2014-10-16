import pytest

from starstoloves.lib.user import user_repository
from starstoloves.lib.track import lastfm_track_repository, spotify_track_repository
from ..models import User, LastfmTrack, SpotifyTrack
from .. import model_repository


pytestmark = pytest.mark.django_db


def test_from_user_returns_model():
    user = user_repository.from_session_key('some_key')
    user_model = model_repository.from_user(user)
    assert isinstance(user_model, User)
    assert user_model.session_key == 'some_key'


def test_from_spotify_track_returns_model():
    track = spotify_track_repository.get_or_create(track_name='some_track', artist_name='some_artist')
    track_model = model_repository.from_spotify_track(track)
    assert isinstance(track_model, SpotifyTrack)
    assert track_model.track_name == 'some_track'
    assert track_model.artist_name == 'some_artist'


def test_from_lastfm_track_returns_model():
    track = lastfm_track_repository.get_or_create(
        url='some_url',
        track_name='some_track',
        artist_name='some_artist'
    )
    track_model = model_repository.from_lastfm_track(track)
    assert isinstance(track_model, LastfmTrack)
    assert track_model.url == 'some_url'
    assert track_model.track_name == 'some_track'
    assert track_model.artist_name == 'some_artist'
