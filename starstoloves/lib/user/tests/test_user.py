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

    def test_it_creates_a_searcher(self, sp_user, LastfmSearcher_patch):
        starred_track_searches(sp_user)
        assert LastfmSearcher_patch.call_count is 1

    def test_it_starts_a_search_for_each_track(self, sp_user, searcher):
        sp_user.starred_tracks = self.starred_tracks
        starred_track_searches(sp_user)
        assert searcher.search.call_args_list == [
            call(self.starred_tracks[0]),
            call(self.starred_tracks[1])
        ]

    def test_it_returns_the_tracks_and_search_queries(self, sp_user, searcher):
        search_returns = []
        def search(track):
            search_returns.append(track['track_name'] + track['artist_name'])
            return search_returns[-1]
        searcher.search.side_effect = search

        sp_user.starred_tracks = self.starred_tracks
        searches = starred_track_searches(sp_user)

        assert searches == [
            {
                'track': self.starred_tracks[0],
                'query': search_returns[0],
            },{
                'track': self.starred_tracks[1],
                'query': search_returns[1],
            }
        ]
