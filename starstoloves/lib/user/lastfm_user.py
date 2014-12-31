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
