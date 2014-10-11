from starstoloves.lib.spotify_session import session as spotify_session


class SpotifyUser:

    def __init__(self, connection):
        self.connection = connection

    @property
    def starred_tracks(self):
        tracks = self._starred_tracks_data
        return tracks

    @property
    def _starred_tracks_data(self):
        starred = self.api_user.starred
        playlist = starred.load().tracks_with_metadata
        tracks = [(item, item.track.load()) for item in playlist]
        track_data = [
            {
                'track_name': track.name,
                'artist_name': track.artists[0].load().name,
                'date_saved': item.create_time,
            }
            for item, track in tracks
        ]
        return track_data

    @property
    def api_user(self):
        user_uri = self.connection.user_uri
        return spotify_session.get_user(user_uri).load()
