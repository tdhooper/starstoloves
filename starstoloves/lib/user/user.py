from datetime import datetime

from starstoloves.lib.connection import (
    spotify_connection_repository,
    lastfm_connection_repository,
)
from starstoloves.lib.track import (
    spotify_playlist_track_repository,
    lastfm_track_repository,
)
from .spotify_user import SpotifyUser
from .lastfm_user import LastfmUser



class User():

    def __init__(self, session_key, loved_tracks=None):
        self.session_key = session_key
        self._loved_tracks = loved_tracks


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


    @property
    def loved_tracks(self):
        if self._loved_tracks:
            return self._loved_tracks

        loved_track_urls = self.lastfm_user.loved_track_urls

        if not loved_track_urls:
            return None

        return [
            lastfm_track_repository.get_or_create(url=url)
            for url in loved_track_urls
        ]


    @loved_tracks.setter
    def loved_tracks(self, value):
        self._loved_tracks = value


    def love_tracks(self, tracks):
        for track in tracks:
            self.lastfm_user.love_track(
                track_name=track.track_name,
                artist_name=track.artist_name,
            )


    @property
    def spotify_user(self):
        connection = spotify_connection_repository.from_user(self)
        return SpotifyUser(connection)


    @property
    def lastfm_user(self):
        connection = lastfm_connection_repository.from_user(self)
        return LastfmUser(connection)
