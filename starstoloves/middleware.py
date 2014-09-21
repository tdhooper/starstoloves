from starstoloves.lib.user import user_repository

class SessionUser:

    def process_request(self, request):
        user = None
        session_key = request.session.session_key
        request.session_user = user_repository.from_session_key(session_key)


from django.http import HttpResponse

class SpotifySession:

    def __init__(self):
        # see startup.py
        self.spotify_session = spotify_session

    def process_request(self, request):
        if not self.spotify_session:
            return HttpResponse('Spotify authentication failed')
