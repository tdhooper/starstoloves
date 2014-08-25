from starstoloves.models import User

class SessionUser:

    def process_request(self, request):
        user = None
        session_key = request.session.session_key
        if session_key:
            user, created = User.objects.get_or_create(session_key=session_key)
        request.session_user = user


from django.http import HttpResponse

class SpotifySession:

    def __init__(self):
        # see startup.py
        self.spotify_session = spotify_session

    def process_request(self, request):
        if not self.spotify_session:
            return HttpResponse('Spotify authentication failed')


from lastfm import lfm
from starstoloves import settings
from starstoloves.lib.connection.lastfm_connection import LastfmConnectionHelper

class LastfmApi:

    def __init__(self):
        self.app = lfm.App(settings.LASTFM['key'], settings.LASTFM['secret'])

    def process_request(self, request):
        request.lastfm_app = self.app
        request.lastfm_connection = LastfmConnectionHelper(request.session_user, self.app)

