import settings
import spotify
from lib import spotify_auth
from django.http import HttpResponse

class SpotifySession:

    def __init__(self):
        config = spotify.Config()
        config.user_agent = settings.SPOTIFY['user_agent']
        config.load_application_key_file(settings.SPOTIFY['key_file'])
        self.spotifySession = spotify.Session(config=config)

        auth = spotify_auth.SpotifyAuth(self.spotifySession);
        username = settings.SPOTIFY['username']
        password = settings.SPOTIFY['password']
        self.success = auth.login(username, password)

    def process_request(self, request):
        if not self.success:
            return HttpResponse('Spotify authentication failed')
        request.spotifySession = self.spotifySession


from lastfm import lfm

class LastfmApp:

    def __init__(self):
        self.app = lfm.App(settings.LASTFM['key'], settings.LASTFM['secret'])

    def process_request(self, request):
        request.lastfmApp = self.app
