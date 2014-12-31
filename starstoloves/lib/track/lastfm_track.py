from starstoloves.lib.comparable import Comparable

class LastfmTrack(Comparable):

    loved = False


    def __init__(self, url, track_name=None, artist_name=None, listeners=None):
        self.url = url
        self.track_name = track_name
        self.artist_name = artist_name
        self.listeners = listeners


    def __eq__(self, other):
        return self.url == other.url



class LastfmPlaylistTrack(LastfmTrack):

    def __init__(self, user, url, added, track_name=None, artist_name=None, listeners=None):
        super().__init__(url, track_name, artist_name, listeners)
        self.user = user
        self.added = added
