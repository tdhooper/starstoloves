from starstoloves.lib.search.searcher import LastfmSearcher
from starstoloves.lib.connection import spotify_connection_repository
from .spotify_user import SpotifyUser


def starred_track_searches(user):
    searcher = LastfmSearcher()
    searches = [
        {
            'track': track,
            'query': searcher.search(track),
        }
        for track in user.starred_tracks
    ]
    return searches


class User():

    def __init__(self, session_key, starred_tracks=None, loved_tracks=None):
        self.session_key = session_key
        self.starred_tracks = starred_tracks
        self.loved_tracks = loved_tracks

    @property
    def starred_tracks(self):
        if self._starred_tracks is not None:
            return self._starred_tracks
        return self.spotify_user.starred_tracks

    @starred_tracks.setter
    def starred_tracks(self, value):
        self._starred_tracks = value

    @property
    def spotify_user(self):
        connection = spotify_connection_repository.from_user(self)
        return SpotifyUser(connection)
