from starstoloves.lib.lastfm import lastfm_app


class LastfmUser:

    def __init__(self, connection):
        self.connection = connection
        lastfm_app.session_key = connection.session_key


    @property
    def loved_tracks(self):
        if not self.connection.is_connected:
            return None

        username = self.connection.username

        loved_tracks_response = lastfm_app.user.get_loved_tracks(username)

        if not 'track' in loved_tracks_response:
            return None

        return [
            {
                'url': track['url'],
                'track_name': track['name'],
                'artist_name': track['artist']['name'],
                'added': int(track['date']['uts']),
            }
            for track in loved_tracks_response['track']
        ]


    def love_track(self, track_name, artist_name, timestamp=None):
        lastfm_app.request('track', 'love', {
            'track': track_name,
            'artist': artist_name,
            'timestamp': timestamp,
        })


    def love_tracks(self, tracks):
        loved_tracks = self.loved_tracks
        for track in tracks:
            if loved_tracks and self._contains_track(track, loved_tracks):
                lastfm_app.track.unlove(
                    artist=track['artist_name'],
                    track=track['track_name'],
                )
            self.love_track(**track)


    def _contains_track(self, a, tracks):
        for b in tracks:
            if self._compare_tracks(a, b):
                return True


    def _compare_tracks(self, a, b):
        return a['artist_name'] == b['artist_name'] and a['track_name'] == b['track_name']
