import pytest

from starstoloves.models import LastfmTrack as LastfmTrackModel
from starstoloves import model_repository
from .. import lastfm_track_repository
from ..lastfm_track import LastfmTrack



pytestmark = pytest.mark.django_db



class TestGetOrCreate:


    def test_returns_a_lastfm_track(self):
        track = lastfm_track_repository.get_or_create(url='some_url')
        assert isinstance(track, LastfmTrack)


    def test_passes_data(self):
        track = lastfm_track_repository.get_or_create(
            url='some_url',
            track_name='some_track',
            artist_name='some_artist',
            listeners=10,
        )
        assert track.url == 'some_url'
        assert track.track_name == 'some_track'
        assert track.artist_name == 'some_artist'
        assert track.listeners == 10


    def test_only_url_is_required(self):
        lastfm_track_repository.get_or_create(url='some_url')


    def test_full_details_can_be_retrieved_with_just_the_url(self):
        lastfm_track_repository.get_or_create(
            url='some_url',
            track_name='some_track',
            artist_name='some_artist',
            listeners=10,
        )
        track = lastfm_track_repository.get_or_create('some_url')
        assert track.url == 'some_url'
        assert track.track_name == 'some_track'
        assert track.artist_name == 'some_artist'
        assert track.listeners == 10


    def test_stores_data_in_db(self):
        lastfm_track_repository.get_or_create(
            url='some_url',
            track_name='some_track',
            artist_name='some_artist',
            listeners=10,
        )
        assert LastfmTrackModel.objects.filter(
            url='some_url',
            track_name='some_track',
            artist_name='some_artist',
            listeners=10,
        ).count() is 1


    def test_does_not_create_multiple_entries_for_url(self):
        lastfm_track_repository.get_or_create(url='some_url')
        lastfm_track_repository.get_or_create(
            url='some_url',
            track_name='some_track',
            artist_name='some_artist',
            listeners=10,
        )
        assert LastfmTrackModel.objects.filter(url='some_url').count() is 1


    def test_adds_new_fields(self):
        lastfm_track_repository.get_or_create(url='some_url')
        lastfm_track_repository.get_or_create(
            url='some_url',
            track_name='some_track',
            artist_name='some_artist',
            listeners=10,
        )
        track = lastfm_track_repository.get_or_create(url='some_url')

        assert track.url == 'some_url'
        assert track.track_name == 'some_track'
        assert track.artist_name == 'some_artist'
        assert track.listeners == 10



class TestFromModel:


    def test_returns_a_lastfm_track(self):
        track = lastfm_track_repository.get_or_create(url='some_url')
        track_model = model_repository.from_lastfm_track(track)
        new_track = lastfm_track_repository.from_model(track_model)
        assert isinstance(new_track, LastfmTrack)


    def test_passes_data(self):
        track = lastfm_track_repository.get_or_create(
            url='some_url',
            track_name='some_track',
            artist_name='some_artist',
            listeners=10,
        )
        track_model = model_repository.from_lastfm_track(track)
        new_track = lastfm_track_repository.from_model(track_model)
        assert new_track.url == 'some_url'
        assert new_track.track_name == 'some_track'
        assert new_track.artist_name == 'some_artist'
        assert new_track.listeners == 10



class TestSave:


    def test_stores_data_in_db(self):
        track = LastfmTrack(
            url='some_url',
            track_name='some_track',
            artist_name='some_artist',
            listeners=10,
        )
        lastfm_track_repository.save(track)
        assert LastfmTrackModel.objects.filter(
            url='some_url',
            track_name='some_track',
            artist_name='some_artist',
            listeners=10,
        ).count() is 1



class TestGet:

    def test_returns_none_on_fail(self):
        assert lastfm_track_repository.get('some_url') == None


    def test_full_details_can_be_retrieved_with_just_the_url(self):
        lastfm_track_repository.get_or_create(
            url='some_url',
            track_name='some_track',
            artist_name='some_artist',
            listeners=10,
        )
        track = lastfm_track_repository.get('some_url')
        assert track.url == 'some_url'
        assert track.track_name == 'some_track'
        assert track.artist_name == 'some_artist'
        assert track.listeners == 10
