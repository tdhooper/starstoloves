from unittest.mock import MagicMock, call

import pytest

from lastfm import lfm

from starstoloves.models import SpotifyTrack, LastfmTrack
from .. import repository
from ..user import User


pytestmark = pytest.mark.django_db


class TestFromSessionKey():

    def test_returns_user(self):
        user = repository.from_session_key('some_key')
        assert isinstance(user, User)

    def test_passes_session_key(self):
        user = repository.from_session_key('some_key')
        assert user.session_key == 'some_key'


class TestSave():

    def test_persists_starred_tracks(self):
        user = repository.from_session_key('some_key')
        track_models = [
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
        user.starred_tracks = track_models
        repository.save(user)

        user = repository.from_session_key('some_key')
        tracks = user.starred_tracks.values()
        assert tracks[0]['track_name'] == 'some_track';
        assert tracks[0]['artist_name'] == 'some_artist';
        assert tracks[1]['track_name'] == 'another_track';
        assert tracks[1]['artist_name'] == 'another_artist';

    def test_persists_loved_tracks(self):
        user = repository.from_session_key('some_key')
        track_models = [
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
        user.loved_tracks = track_models
        repository.save(user)

        user = repository.from_session_key('some_key')
        tracks = user.loved_tracks.values()
        assert tracks[0]['track_name'] == 'some_track';
        assert tracks[0]['artist_name'] == 'some_artist';
        assert tracks[0]['url'] == 'some_url';
        assert tracks[1]['track_name'] == 'another_track';
        assert tracks[1]['artist_name'] == 'another_artist';
        assert tracks[1]['url'] == 'another_url';
