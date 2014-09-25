import pytest

from starstoloves.models import SpotifyTrack as SpotifyTrackModel
from .. import spotify_track_repository
from ..spotify_track import SpotifyTrack


pytestmark = pytest.mark.django_db


class TestGetOrCreate:

    def test_returns_a_spotify_track(self):
        track = spotify_track_repository.get_or_create(track_name='some_track', artist_name='some_artist')
        assert isinstance(track, SpotifyTrack)

    def test_passes_track_and_artist_name(self):
        track = spotify_track_repository.get_or_create(track_name='some_track', artist_name='some_artist')
        assert track.track_name == 'some_track'
        assert track.artist_name == 'some_artist'

    def test_stores_track_and_artist_name_in_db(self):
        track = spotify_track_repository.get_or_create(track_name='some_track', artist_name='some_artist')
        assert SpotifyTrackModel.objects.filter(track_name='some_track', artist_name='some_artist').count() is 1


class TestGetModel:

    def test_returns_model(self):
        track = spotify_track_repository.get_or_create(track_name='some_track', artist_name='some_artist')
        track_model = spotify_track_repository.get_model(track)
        assert isinstance(track_model, SpotifyTrackModel)
        assert track_model.track_name == 'some_track'
        assert track_model.artist_name == 'some_artist'
