from unittest.mock import MagicMock, call

import pytest

from lastfm import lfm

from ..spotify_user import SpotifyUser
from ..user import starred_track_searches


@pytest.fixture
def sp_user():
    return MagicMock(spec=SpotifyUser).return_value

@pytest.fixture
def LastfmSearcher_patch(create_patch):
    return create_patch('starstoloves.lib.user.user.LastfmSearcher')

@pytest.fixture
def searcher(LastfmSearcher_patch):
    return LastfmSearcher_patch.return_value


class TestStarredTrackSearches:

    starred_tracks = [
            {
                'track_name': 'some_track',
                'artist_name': 'some_artist',
            },{
                'track_name': 'another_track',
                'artist_name': 'another_artist',
            }
        ]

    def test_it_creates_a_searcher(self, user, LastfmSearcher_patch):
        user.starred_tracks = self.starred_tracks
        starred_track_searches(user)
        assert LastfmSearcher_patch.call_count is 1

    def test_it_starts_a_search_for_each_track(self, user, searcher):
        user.starred_tracks = self.starred_tracks
        starred_track_searches(user)
        assert searcher.search.call_args_list == [
            call(self.starred_tracks[0]),
            call(self.starred_tracks[1])
        ]

    def test_it_returns_the_tracks_and_search_queries(self, user, searcher):
        search_returns = []
        def search(track):
            search_returns.append(track['track_name'] + track['artist_name'])
            return search_returns[-1]
        searcher.search.side_effect = search

        user.starred_tracks = self.starred_tracks
        searches = starred_track_searches(user)

        assert searches == [
            {
                'track': self.starred_tracks[0],
                'query': search_returns[0],
            },{
                'track': self.starred_tracks[1],
                'query': search_returns[1],
            }
        ]


from unittest.mock import PropertyMock

from ..user import User


pytestmark = pytest.mark.django_db



@pytest.fixture
def spotify_connection_repository(create_patch):
    return create_patch('starstoloves.lib.user.user.spotify_connection_repository')

@pytest.fixture
def SpotifyUser(create_patch):
    return create_patch('starstoloves.lib.user.user.SpotifyUser')

@pytest.fixture
def spotify_user(SpotifyUser):
    return SpotifyUser.return_value


class TestUser:

    def test_returns_values_it_was_created_with(self):
        user = User('some_key', 'some_starred_tracks', 'some_loved_tracks')
        assert user.session_key == 'some_key'
        assert user.starred_tracks == 'some_starred_tracks'
        assert user.loved_tracks == 'some_loved_tracks'


    def test_spotify_user_is_created_with_spotify_connection(self, user, SpotifyUser, spotify_connection_repository):
        spotify_user = user.spotify_user
        assert spotify_connection_repository.from_user.call_args == call(user)
        assert SpotifyUser.call_args == call(spotify_connection_repository.from_user.return_value)
        assert spotify_user is SpotifyUser.return_value


    def test_starred_tracks_proxies_to_spotify_user(self, user, spotify_user):
        assert user.starred_tracks is spotify_user.starred_tracks


    def test_starred_tracks_can_be_set(self, user):
        user.starred_tracks = 'some_starred_tracks'
        assert user.starred_tracks == 'some_starred_tracks'
