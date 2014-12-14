from uuid import uuid4
from unittest.mock import MagicMock, call, patch

import pytest

from django.core.urlresolvers import reverse
from django.conf import settings

from celery.result import AsyncResult

from starstoloves.lib.user.tests.fixtures.spotify_user_fixtures import *
from starstoloves.lib.search.query import LastfmQuery
from starstoloves.lib.track.lastfm_track import LastfmTrack
from starstoloves.lib.user.user import User
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


    def test_returns_tracks(self, client, search_lastfm):
        response = client.get(reverse('index'))

        assert response.context['tracks'][0]['track'].track_name == 'some_track'
        assert response.context['tracks'][0]['track'].artist_name == 'some_artist'
        assert response.context['tracks'][0]['track'].added.timestamp() == 123456

        assert response.context['tracks'][1]['track'].track_name == 'another_track'
        assert response.context['tracks'][1]['track'].artist_name == 'another_artist'
        assert response.context['tracks'][1]['track'].added.timestamp() == 789012


    def test_returns_results(self, client, separate_search_patch, combined_search_patch):
        track_almost = LastfmTrack('some_url_1', 'some_track_almost', 'some_artist_almost')
        track_nope = LastfmTrack('some_url_2', 'nope', 'nope')
        track_match = LastfmTrack('some_url_3', 'some_track', 'some_artist')
        track_reversed = LastfmTrack('some_url_4', 'some_artist', 'some_track')

        separate_search_patch.return_value = [track_almost, track_nope]
        combined_search_patch.return_value = [track_almost, track_match, track_reversed]

        response = client.get(reverse('index'))
        assert response.context['tracks'][0]['results'] == [track_match, track_almost, track_reversed, track_nope]



@pytest.mark.usefixtures("lastfm_connected")
@pytest.mark.usefixtures("spotify_connected")
@pytest.mark.usefixtures("spotify_user_with_starred")
class TestLoveTracks():

    def test_redirects_to_index(self, client):
        response = client.post(reverse('love_tracks'), follow=True);
        assert response.redirect_chain[0][0] == 'http://testserver' + reverse('index')


    def test_loves_checked_results(self, client, separate_search_patch):
        tracks = [
            LastfmTrack('some_url_a', 'some_track_a', 'some_artist_a'),
            LastfmTrack('some_url_b', 'some_track_b', 'some_artist_b'),
            LastfmTrack('some_url_c', 'some_track_c', 'some_artist_c'),
        ]
        separate_search_patch.return_value = tracks
        client.get(reverse('index'))

        with patch('starstoloves.middleware.user_repository') as user_repository:

            session_user = MagicMock(spec=User)
            user_repository.from_session_key.return_value = session_user

            client.post(reverse('love_tracks'), {
                'love_tracks': [
                    'some_url_a',
                    'some_url_b',
                ]
            });

            loved_tracks = session_user.love_tracks.call_args[0][0]
            assert len(loved_tracks) is 2
            assert tracks[0] in loved_tracks
            assert tracks[1] in loved_tracks


    # TODO: Return a warning when requested tracks weren't loved
    def test_ignores_junk_results(self, client):
        with patch('starstoloves.middleware.user_repository') as user_repository:

            session_user = MagicMock(spec=User)
            user_repository.from_session_key.return_value = session_user

            client.post(reverse('love_tracks'), {
                'love_tracks': [
                    'not_a_track'
                ]
            });

            assert session_user.love_tracks.call_args[0][0] == []


@pytest.mark.usefixtures("spotify_connected")
@pytest.mark.usefixtures('has_searches')
def test_disconnect_spotify_clears_searches(client, searches):
    response = client.get(reverse('disconnect_spotify'), follow=True)
    assert searches[0]['query'].stop.call_count is 1
    assert searches[1]['query'].stop.call_count is 1
