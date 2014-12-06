from uuid import uuid4
from unittest.mock import MagicMock, call

import pytest

from django.core.urlresolvers import reverse
from django.conf import settings

from celery.result import AsyncResult

from starstoloves.lib.user.tests.fixtures.spotify_user_fixtures import *
from starstoloves.lib.search.query import LastfmQuery
from starstoloves.lib.track.lastfm_track import LastfmTrack
from .fixtures.connection_fixtures import *


pytestmark = pytest.mark.django_db


@pytest.fixture
def search_lastfm(create_patch):
    search_lastfm = create_patch('starstoloves.lib.search.query.search_lastfm')

    def new_async(*args):
        result = MagicMock(spec=AsyncResult).return_value
        result.id = uuid4().hex
        return result

    search_lastfm.delay.side_effect = new_async
    return search_lastfm


@pytest.fixture
def separate_search_patch(create_patch):
    return create_patch('starstoloves.lib.search.multi.separate_search_strategy')


@pytest.fixture
def combined_search_patch(create_patch):
    return create_patch('starstoloves.lib.search.multi.combined_search_strategy')


@pytest.fixture
def get_searches_patch(create_patch):
    return create_patch('starstoloves.views.main.get_searches')


@pytest.fixture
def searches():
    return [
        {'query': MagicMock(spec=LastfmQuery)},
        {'query': MagicMock(spec=LastfmQuery)}
    ]


@pytest.fixture
def has_searches(get_searches_patch, searches):
    get_searches_patch.return_value = searches


@pytest.mark.usefixtures("lastfm_connected")
@pytest.mark.usefixtures("spotify_connected")
@pytest.mark.usefixtures("spotify_user_with_starred")
class TestIndex():

    def test_starts_a_search_for_each_starred_track(self, client, search_lastfm):
        client.get(reverse('index'))
        assert search_lastfm.delay.call_args_list == [
            call('some_track', 'some_artist'),
            call('another_track', 'another_artist')
        ]


    def test_returns_results(self, client, separate_search_patch, combined_search_patch):
        track_almost = LastfmTrack('some_url_1', 'some_track_almost', 'some_artist_almost')
        track_nope = LastfmTrack('some_url_2', 'nope', 'nope')
        track_match = LastfmTrack('some_url_3', 'some_track', 'some_artist')
        track_reversed = LastfmTrack('some_url_4', 'some_artist', 'some_track')

        separate_search_patch.return_value = [track_almost, track_nope]
        combined_search_patch.return_value = [track_almost, track_match, track_reversed]

        response = client.get(reverse('index'))
        assert response.context['tracks'][0]['results'] == [track_match, track_almost, track_reversed, track_nope]


@pytest.mark.usefixtures("spotify_connected")
@pytest.mark.usefixtures('has_searches')
def test_disconnect_spotify_clears_searches(client, searches):
    response = client.get(reverse('disconnect_spotify'), follow=True)
    assert searches[0]['query'].stop.call_count is 1
    assert searches[1]['query'].stop.call_count is 1
