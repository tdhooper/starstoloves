from starstoloves.lib.comparable import Comparable

class LastfmTrack(Comparable):

    def __init__(self, url, track_name=None, artist_name=None, listeners=None):
        self.url = url
        self.track_name = track_name
        self.artist_name = artist_name
        self.listeners = listeners

    # TODO: Only use URL for comparison
