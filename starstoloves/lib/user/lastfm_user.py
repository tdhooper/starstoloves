from starstoloves.lib.lastfm import lastfm_app


class LastfmUser:

    def __init__(self, connection):
        self.connection = connection
        lastfm_app.session_key = connection.session_key


    @property
    def loved_track_urls(self):
        username = self.connection.username
        loved_tracks_response = lastfm_app.user.get_loved_tracks(username)
        urls = [track['url'] for track in loved_tracks_response['track']]
        return urls


    def love_track(self, track_name, artist_name):
        print(track_name, artist_name)
        lastfm_app.track.love(track=track_name, artist=artist_name)
