from starstoloves.lib.connection import lastfm_connection_repository
from starstoloves.lib.lastfm import lastfm_app


class LastfmUser:

    def __init__(self, user):
        self.user = user

    @property
    def connection(self):
        return lastfm_connection_repository.from_user(self.user)

    @property
    def loved_track_urls(self):
        username = self.connection.username
        loved_tracks_response = lastfm_app.user.get_loved_tracks(username)
        urls = [track['url'] for track in loved_tracks_response['track']]
        return urls
