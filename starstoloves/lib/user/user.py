from datetime import datetime

from starstoloves.lib.search.searcher import LastfmSearcher
from starstoloves.lib.connection import spotify_connection_repository
from starstoloves.lib.track import spotify_playlist_track_repository
from .spotify_user import SpotifyUser


def starred_track_searches(user):
    searcher = LastfmSearcher()
    searches = [
        {
            'track': track,
            'query': searcher.search(track),
        }
        for track in [
            {
                'track_name': playlist_track.track_name,
                'artist_name': playlist_track.artist_name,
            }
            for playlist_track in user.starred_tracks
        ]
    ]
    return searches


class User():

    def __init__(self, session_key, loved_tracks=None):
        self.session_key = session_key
        self.loved_tracks = loved_tracks

    @property
    def starred_tracks(self):
        tracks = spotify_playlist_track_repository.for_user(self)
        if len(tracks) is not 0:
            return tracks

        return [
            spotify_playlist_track_repository.get_or_create(
                user=self,
                track_name=track['track_name'],
                artist_name=track['artist_name'],
                added=datetime.fromtimestamp(track['date_saved'])
            )
            for track in self.spotify_user.starred_tracks
        ]

    @property
    def spotify_user(self):
        connection = spotify_connection_repository.from_user(self)
        return SpotifyUser(connection)
