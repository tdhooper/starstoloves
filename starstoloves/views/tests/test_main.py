from datetime import datetime
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
from starstoloves.lib.mapping import TrackMapping
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
def get_correction_patch(create_patch):
    return create_patch('starstoloves.lib.search.multi.get_correction')


@pytest.fixture
def lastfm_user(create_patch):
    instance = create_patch('starstoloves.lib.user.user.LastfmUser').return_value
    instance.loved_tracks = None
    return instance


@pytest.fixture
def some_track_results():
    return {
        'almost': LastfmTrack('some_url_1', 'some_track_almost', 'some_artist_almost'),
        'nope': LastfmTrack('some_url_2', 'nope', 'nope'),
        'match': LastfmTrack('some_url_3', 'some_track', 'some_artist'),
        'reversed': LastfmTrack('some_url_4', 'some_artist', 'some_track'),
    }


@pytest.fixture
def another_track_results():
    return {
        'match': LastfmTrack('some_url_5', 'another_track', 'another_artist'),
    }


@pytest.fixture
def has_results(
    spotify_user_with_starred,
    separate_search_patch,
    combined_search_patch,
    get_correction_patch,
    some_track_results,
    another_track_results
):
    def separate_search(track_name, artist_name):
        return {
            'some_track': [
                some_track_results['almost'],
                some_track_results['nope'],
            ],
            'another_track': [
                another_track_results['match'],
            ],
        }[track_name]

    def combined_search(track_name, artist_name):
        return {
            'some_track': [
                some_track_results['almost'],
                some_track_results['match'],
                some_track_results['reversed'],
            ],
        }[track_name]

    separate_search_patch.side_effect = separate_search
    combined_search_patch.side_effect = combined_search
    get_correction_patch.return_value = None


@pytest.fixture
def session_user(create_patch):
    user = MagicMock(spec=User)()
    repo = create_patch('starstoloves.middleware.user_repository')
    repo.from_session_key.return_value = user
    return user



@pytest.mark.usefixtures("lastfm_connected")
@pytest.mark.usefixtures("spotify_connected")
@pytest.mark.usefixtures("has_results")
class TestIndex():

    def test_starts_a_search_for_each_starred_track(self, client, search_lastfm):
        client.get(reverse('index'))
        assert search_lastfm.delay.call_args_list == [
            call('another_track', 'another_artist'),
            call('some_track', 'some_artist'),
        ]


    def test_returns_TrackMappings(self, client, search_lastfm):
        response = client.get(reverse('index'))

        assert isinstance(response.context['mappings'][0], TrackMapping)
        assert response.context['mappings'][0].track.track_name == 'another_track'
        assert response.context['mappings'][0].track.artist_name == 'another_artist'
        assert response.context['mappings'][0].track.added.timestamp() == 789012

        assert isinstance(response.context['mappings'][1], TrackMapping)
        assert response.context['mappings'][1].track.track_name == 'some_track'
        assert response.context['mappings'][1].track.artist_name == 'some_artist'
        assert response.context['mappings'][1].track.added.timestamp() == 123456


    def test_returns_results(self, client, some_track_results):
        response = client.get(reverse('index'))
        assert response.context['mappings'][1].results == [
            {
                'track': some_track_results['match'],
                'loved': False,
                'love': True,
            },{
                'track': some_track_results['almost'],
                'loved': False,
                'love': False,
            },{
                'track': some_track_results['reversed'],
                'loved': False,
                'love': False,
            },{
                'track': some_track_results['nope'],
                'loved': False,
                'love': False,
            }
        ]


    def test_bumps_loved_tracks_to_the_top_and_marks_them(self, client, lastfm_user, some_track_results):
        lastfm_user.loved_tracks = [
            {
                'url': 'some_url_3',
                'added': 123
            },
            {
                'url': 'some_url_4',
                'added': 456
            },
        ]

        response = client.get(reverse('index'))
        assert response.context['mappings'][1].results == [
            {
                'track': some_track_results['match'],
                'loved': datetime.fromtimestamp(123),
                'love': False,
            },{
                'track': some_track_results['reversed'],
                'loved': datetime.fromtimestamp(456),
                'love': False,
            },{
                'track': some_track_results['almost'],
                'loved': False,
                'love': False,
            },{
                'track': some_track_results['nope'],
                'loved': False,
                'love': False,
            }
        ]



@pytest.mark.usefixtures("lastfm_connected")
@pytest.mark.usefixtures("spotify_connected")
@pytest.mark.usefixtures("has_results")
class TestLoveTracks():

    def test_redirects_to_index(self, client):
        response = client.post(reverse('love_tracks'), follow=True)
        assert response.redirect_chain[0][0] == 'http://testserver' + reverse('index')


    def test_loves_checked_results(self, client, lastfm_user, some_track_results, another_track_results):
        response = client.get(reverse('index'))

        client.post(reverse('love_tracks'), {
            response.context['mappings'][0].id: [
                'some_url_5',
            ],
            response.context['mappings'][1].id: [
                'some_url_1',
                'some_url_2',
            ],
        });

        loved_tracks = lastfm_user.love_tracks.call_args[0][0]

        assert len(loved_tracks) is 3

        assert {
            'track_name': some_track_results['almost'].track_name,
            'artist_name': some_track_results['almost'].artist_name,
            'timestamp': 123456,
        } in loved_tracks

        assert {
            'track_name': some_track_results['nope'].track_name,
            'artist_name': some_track_results['nope'].artist_name,
            'timestamp': 123456,
        } in loved_tracks

        assert {
            'track_name': another_track_results['match'].track_name,
            'artist_name': another_track_results['match'].artist_name,
            'timestamp': 789012,
        } in loved_tracks


    def test_gets_fresh_loved_tracks(self, client, lastfm_user):

        lastfm_user.loved_tracks = [
            {
                'url': 'some_url_3',
                'added': 123
            }
        ]

        def love_tracks(*args, **kwargs):
            lastfm_user.loved_tracks = [
                {
                    'url': 'some_url_3',
                    'added': 123
                },
                {
                    'url': 'some_url_4',
                    'added': 456
                },
            ]
        lastfm_user.love_tracks.side_effect = love_tracks

        response = client.get(reverse('index'))
        assert response.context['mappings'][1].results[0]['loved'] is not False
        assert response.context['mappings'][1].results[1]['loved'] is False

        response = client.post(reverse('love_tracks'), {
            response.context['mappings'][1].id: [
                'some_url_4',
            ],
        }, follow=True);
        assert response.context['mappings'][1].results[0]['loved'] is not False
        assert response.context['mappings'][1].results[1]['loved'] is not False


    # TODO: Return a warning when requested tracks weren't loved
    def test_ignores_junk_results(self, client, lastfm_user):
        response = client.get(reverse('index'))

        client.post(reverse('love_tracks'), {
            response.context['mappings'][0].id: [
                'not_a_track',
            ],
        });

        assert lastfm_user.love_tracks.call_count is 0


    def test_ignores_junk_ids(self, client, lastfm_user):
        response = client.get(reverse('index'))

        client.post(reverse('love_tracks'), {
            'not_an_id': [
                'some_url_4',
            ],
        });

        assert lastfm_user.love_tracks.call_count is 0



@pytest.fixture
def queries():
    return {
        'some_track': MagicMock(spec=LastfmQuery).return_value,
        'another_track': MagicMock(spec=LastfmQuery).return_value,
    }


@pytest.fixture
def LastfmQuery_patch(create_patch, queries):

    def new_LastfmQuery(repository, track_name, artist_name=None, async_result=None, results=None):
        return queries[track_name]

    patch = create_patch('starstoloves.lib.search.query_repository.LastfmQuery')
    patch.side_effect = new_LastfmQuery
    return patch



@pytest.mark.usefixtures("spotify_connected")
@pytest.mark.usefixtures("lastfm_connected")
class TestDisconnectSpotify():

    @pytest.mark.usefixtures('LastfmQuery_patch')
    @pytest.mark.usefixtures("spotify_user_with_starred")
    def test_clears_searches(self, client, queries):
        client.get(reverse('disconnect_spotify'), follow=True)
        assert queries['some_track'].stop.call_count is 1
        assert queries['another_track'].stop.call_count is 1


    def test_clears_starred_tracks(self, client, session_user):
        client.get(reverse('disconnect_spotify'), follow=True)
        assert session_user.reload_starred_tracks.call_count is 1



@pytest.mark.usefixtures("spotify_connected")
@pytest.mark.usefixtures("lastfm_connected")
def test_disconnect_lastfm_clears_loved_tracks(client, queries, session_user):
    client.get(reverse('disconnect_lastfm'))
    assert session_user.reload_loved_tracks.call_count is 1



@pytest.mark.usefixtures("spotify_connected")
@pytest.mark.usefixtures("lastfm_connected")
@pytest.mark.usefixtures("spotify_session")
class TestReloadSpotify():

    def test_reloads_starred_tracks(self, client, session_user):
        response = client.get(reverse('reload_spotify'), follow=True)
        assert session_user.reload_starred_tracks.call_count is 1


    def test_redirects_to_index(self, client):
        response = client.get(reverse('reload_spotify'), follow=True)
        assert response.redirect_chain[0][0] == 'http://testserver' + reverse('index')



@pytest.mark.usefixtures("spotify_connected")
@pytest.mark.usefixtures("lastfm_connected")
@pytest.mark.usefixtures("spotify_session")
class TestReloadLastfm():

    def test_reloads_loved_tracks(self, client, session_user):
        response = client.get(reverse('reload_lastfm'), follow=True)
        assert session_user.reload_loved_tracks.call_count is 1


    def test_redirects_to_index(self, client):
        response = client.get(reverse('reload_lastfm'), follow=True)
        assert response.redirect_chain[0][0] == 'http://testserver' + reverse('index')
