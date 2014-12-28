import spotify
import threading

class SpotifyAuth:

    def __init__(self, spotifySession):
        self.spotifySession = spotifySession

    def login(self, username, password):

        logged_in_event = threading.Event()

        def logged_in_listener(spotifySession, error_type):
            if error_type != 0:
                logged_in_event.set()
            else:
                spotifySession.process_events()
                while spotifySession.connection_state != spotify.ConnectionState.LOGGED_IN:
                    spotifySession.process_events()
                logged_in_event.set()

        loop = spotify.EventLoop(self.spotifySession)
        loop.start()
        self.spotifySession.on(spotify.SessionEvent.LOGGED_IN, logged_in_listener)

        self.spotifySession.login(username, password)

        logged_in_event.wait(timeout=5)

        if logged_in_event.is_set():
            return self.isReady()


    def isReady(self):
        if self.spotifySession.connection_state == spotify.ConnectionState.LOGGED_IN:
            return True
        else:
            return False