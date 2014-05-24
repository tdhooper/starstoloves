import settings
from django.http import HttpResponse
from views.helpers.spotify_connection import SpotifyConnectionHelper

class SpotifySession:

    def __init__(self):
        # see startup.py
        self.spotify_session = spotify_session

    def process_request(self, request):
        if not self.spotify_session:
            return HttpResponse('Spotify authentication failed')
        request.spotify_session = self.spotify_session
        request.spotify_connection = SpotifyConnectionHelper(request.session, self.spotify_session)


from lastfm import lfm
from views.helpers.lastfm_connection import LastfmConnectionHelper

class LastfmApi:

    def __init__(self):
        self.app = lfm.App(settings.LASTFM['key'], settings.LASTFM['secret'])

    def process_request(self, request):
        request.lastfm_api = self.app
        request.lastfm_connection = LastfmConnectionHelper(request.session, self.app)
