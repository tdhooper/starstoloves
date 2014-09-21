from starstoloves.lib.connection import lastfm_connection_repository
from starstoloves.lib.lastfm import lastfm_app
from starstoloves.models import LastfmTrack
from . import user_repository


class LastfmUser:

    def __init__(self, user):
        self.user = user

    @property
    def connection(self):
        return lastfm_connection_repository.from_user(self.user)

    @property
    def loved_track_urls(self):
        urls = self.retrieve_loved_track_urls()
        if urls:
            return urls
        urls = self.loved_track_urls_data()
        self.store_loved_track_urls(urls)
        return urls

    def store_loved_track_urls(self, urls):
        tracks = [
            LastfmTrack.objects.get_or_create(url=url)[0]
            for url in urls
        ]
        self.user.loved_tracks = tracks
        user_repository.save(self.user)

    def retrieve_loved_track_urls(self):
        if not self.user.loved_tracks:
            return None
        urls = [track.url for track in self.user.loved_tracks]
        return urls

    def loved_track_urls_data(self):
        username = self.connection.username
        loved_tracks_response = lastfm_app.user.get_loved_tracks(username)
        urls = [track['url'] for track in loved_tracks_response['track']]
        return urls
