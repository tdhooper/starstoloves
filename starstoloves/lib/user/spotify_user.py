from datetime import datetime

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
                    'date_saved': int(datetime.strptime(added, '%Y-%m-%dT%H:%M:%SZ').timestamp()) if added else 0,
                })
            result = self.api.next(result)

        return tracks


    @property
    def api(self):
        return Spotify(auth=self.connection.token)
