class SpotifyTrack(object):

    def __init__(self, track_name, artist_name):
        self.track_name = track_name
        self.artist_name = artist_name


class SpotifyPlaylistTrack(SpotifyTrack):

    def __init__(self, user, track_name, artist_name, added):
        super().__init__(track_name, artist_name)
        self.user = user
        self.added = added
