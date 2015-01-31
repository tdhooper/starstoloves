from datetime import datetime, timezone

from dateutil.parser import parse

from spotipy import Spotify


class SpotifyUser:

    def __init__(self, connection):
        self.connection = connection

    @property
    def starred_tracks(self):
        result = self.api.user_playlist(self.connection.username)
        result = result['tracks']
        tracks = []

        while result:
            for track in result['items']:
                added = track['added_at']
                tracks.append({
                    'track_name': track['track']['name'],
                    'artist_name': track['track']['artists'][0]['name'],
                    'date_saved': parse(added) if added else datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                })
            result = self.api.next(result)

        return tracks


    @property
    def api(self):
        return Spotify(auth=self.connection.token)
