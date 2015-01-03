import functools
from datetime import datetime

from starstoloves.lib.repository import RepositoryItem
from starstoloves.lib.connection import (
    spotify_connection_repository,
    lastfm_connection_repository,
)
from starstoloves.lib.track import (
    spotify_playlist_track_repository,
    lastfm_playlist_track_repository,
)
from .spotify_user import SpotifyUser
from .lastfm_user import LastfmUser


class User(RepositoryItem):

    def __init__(self, session_key, **kwargs):
        self.session_key = session_key
        super().__init__(**kwargs)


    @property
    def starred_tracks(self):
        # TODO: Make this work like LastfmQuery#results, using a repository
        # save method so it hides the external repository access
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


    @functools.lru_cache(maxsize=None)
    def loved_tracks(self):
        # TODO: Make this work like LastfmQuery#results, using a repository
        # save method so it hides the external repository access
        tracks = lastfm_playlist_track_repository.for_user(self)
        if len(tracks) is not 0:
            return tracks

        loved_tracks_data = self.lastfm_user.loved_tracks

        if not loved_tracks_data:
            return []

        return [
            lastfm_playlist_track_repository.get_or_create(
                user=self,
                url=track['url'],
                added=datetime.fromtimestamp(track['added'])
            )
            for track in loved_tracks_data
        ]


    def reload_starred_tracks(self):
        spotify_playlist_track_repository.clear_user(self)


    def reload_loved_tracks(self):
        self.loved_tracks.cache_clear()
        lastfm_playlist_track_repository.clear_user(self)


    def love_track(self, track, timestamp=None):
        self.lastfm_user.love_track(
            track_name=track.track_name,
            artist_name=track.artist_name,
            timestamp=timestamp,
        )


    @property
    def spotify_user(self):
        connection = spotify_connection_repository.from_user(self)
        return SpotifyUser(connection)


    @property
    def lastfm_user(self):
        connection = lastfm_connection_repository.from_user(self)
        return LastfmUser(connection)
