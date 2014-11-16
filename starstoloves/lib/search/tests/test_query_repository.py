from unittest.mock import call

import pytest

from starstoloves.models import LastfmSearch as LastfmSearchModel
from starstoloves.lib.track import lastfm_track_repository
from .. import query_repository
from ..query import LastfmQuery
from .fixtures import *


pytestmark = pytest.mark.django_db




class TestGetOrCreate:


    def test_returns_LastfmQuery_with_given_arguments(self):
        query = query_repository.get_or_create('some_track', 'some_artist')
        assert isinstance(query, LastfmQuery)
        assert query.track_name is 'some_track'
        assert query.artist_name is 'some_artist'


    def test_creates_db_entry(self):
        query = query_repository.get_or_create('some_track', 'some_artist')
        assert LastfmSearchModel.objects.filter(
            track_name='some_track',
            artist_name='some_artist'
        ).count() is 1




class TestSave:


    def test_creates_db_entry(self, search_lastfm, async_result):
        search_lastfm.delay.return_value = async_result
        query = LastfmQuery(query_repository, 'some_track', 'some_artist')
        query_repository.save(query)
        assert LastfmSearchModel.objects.filter(
            track_name='some_track',
            artist_name='some_artist'
        ).count() is 1


    def test_persists_async_result_id(self, async_result):
        query = LastfmQuery(query_repository, 'some_track', 'some_artist', async_result)
        query_repository.save(query)
        new_query = query_repository.get_or_create('some_track', 'some_artist')
        assert new_query.async_result.id == 'some_id'


    def test_persists_results(self):
        tracks = [
            lastfm_track_repository.get_or_create(
                track_name='some_track',
                artist_name='some_artist',
                url='some_url'
            ),
            lastfm_track_repository.get_or_create(
                track_name='another_track',
                artist_name='another_artist',
                url='another_url'
            )
        ]
        query = LastfmQuery(query_repository, track_name='some_track', artist_name='some_artist', results=tracks)
        query_repository.save(query)
        new_query = query_repository.get_or_create('some_track', 'some_artist')
        assert new_query.results == tracks
