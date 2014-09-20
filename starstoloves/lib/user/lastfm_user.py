from starstoloves.lib.connection.lastfm_connection import LastfmConnectionHelper
from starstoloves.lib.lastfm import lastfm_app
from starstoloves.models import LastfmTrack
from . import repository


class LastfmUser:

    def __init__(self, user):
        self.user = user

    @property
    def connection(self):
        return LastfmConnectionHelper(self.user, lastfm_app)

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
        repository.save(self.user)

    def retrieve_loved_track_urls(self):
        if not self.user.loved_tracks:
            return None
        urls = [track.url for track in self.user.loved_tracks]
        return urls

    def loved_track_urls_data(self):
        username = self.connection.get_username()
        loved_tracks_response = lastfm_app.user.get_loved_tracks(username)
        urls = [track['url'] for track in loved_tracks_response['track']]
        return urls
