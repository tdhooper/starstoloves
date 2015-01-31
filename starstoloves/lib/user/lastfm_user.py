from datetime import datetime, timezone

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
        tracks = []
        total_pages = 1
        page = 0

        while page < total_pages:
            page += 1
            response = lastfm_app.user.get_loved_tracks(user=username, page=page)

            try:
                tracks += [
                    {
                        'url': track['url'],
                        'track_name': track['name'],
                        'artist_name': track['artist']['name'],
                        'added': datetime.fromtimestamp(int(track['date']['uts']), tz=timezone.utc),
                    }
                    for track in response['track']
                ]

                total_pages = int(response['@attr']['totalPages'])

            except KeyError:
                break

        return tracks or None


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
