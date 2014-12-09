from datetime import datetime
from unittest.mock import MagicMock, call

import pytest

from lastfm import lfm

from starstoloves.lib.track.spotify_track import SpotifyPlaylistTrack
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

@pytest.fixture
def mock_user():
    return MagicMock()

@pytest.fixture
def starred_tracks(mock_user):
    return [
        SpotifyPlaylistTrack(
            user=mock_user,
            track_name='some_track',
            artist_name='some_artist',
            added=datetime.fromtimestamp(123)
        ),
        SpotifyPlaylistTrack(
            user=mock_user,
            track_name='another_track',
            artist_name='another_artist',
            added=datetime.fromtimestamp(456)
        )
    ]


class TestStarredTrackSearches:

    def test_it_creates_a_searcher(self, mock_user, starred_tracks, LastfmSearcher_patch):
        mock_user.starred_tracks = starred_tracks
        starred_track_searches(mock_user)
        assert LastfmSearcher_patch.call_count is 1

    def test_it_starts_a_search_for_each_track(self, mock_user, starred_tracks, searcher):
        mock_user.starred_tracks = starred_tracks
        starred_track_searches(mock_user)
        assert searcher.search.call_args_list == [
            call(starred_tracks[0]),
            call(starred_tracks[1]),
        ]

    def test_it_returns_the_tracks_and_search_queries(self, mock_user, starred_tracks, searcher):
        search_returns = []
        def search(track):
            search_returns.append(track.track_name + track.artist_name)
            return search_returns[-1]
        searcher.search.side_effect = search

        mock_user.starred_tracks = starred_tracks
        searches = starred_track_searches(mock_user)

        assert searches == [
            {
                'track': starred_tracks[0],
                'query': search_returns[0],
            },{
                'track': starred_tracks[1],
                'query': search_returns[1],
            }
        ]


from unittest.mock import PropertyMock

from ..user import User
from starstoloves.lib.user import user_repository


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
        user = User('some_key', 'some_loved_tracks')
        assert user.session_key == 'some_key'
        assert user.loved_tracks == 'some_loved_tracks'


class TestUserStarredTracks:

    starred_tracks = [
            {
                'track_name': 'some_track',
                'artist_name': 'some_artist',
                'date_saved': 123,
            }
        ]


    def test_spotify_user_is_created_with_spotify_connection(self, user, SpotifyUser, spotify_connection_repository):
        spotify_user = user.spotify_user
        assert spotify_connection_repository.from_user.call_args == call(user)
        assert SpotifyUser.call_args == call(spotify_connection_repository.from_user.return_value)
        assert spotify_user is SpotifyUser.return_value


    def test_returns_SpotifyPlaylistTracks(self, user, spotify_user):
        spotify_user.starred_tracks = self.starred_tracks
        assert isinstance(user.starred_tracks[0], SpotifyPlaylistTrack)


    def test_uses_starred_tracks_data_from_spotify_user(self, user, spotify_user):
        spotify_user.starred_tracks = self.starred_tracks
        assert user.starred_tracks[0].user == user
        assert user.starred_tracks[0].track_name == 'some_track'
        assert user.starred_tracks[0].artist_name == 'some_artist'
        assert user.starred_tracks[0].added.timestamp() == 123


    def test_stores_starred_tracks(self, user, spotify_user):
        starred_tracks_property = PropertyMock(return_value=self.starred_tracks)
        type(spotify_user).starred_tracks = starred_tracks_property

        user.starred_tracks
        new_user = user_repository.from_session_key('some_key')
        starred_tracks = new_user.starred_tracks

        assert starred_tracks[0].user == new_user
        assert starred_tracks[0].track_name == 'some_track'
        assert starred_tracks[0].artist_name == 'some_artist'
        assert starred_tracks[0].added.timestamp() == 123

        assert starred_tracks_property.call_count is 1
