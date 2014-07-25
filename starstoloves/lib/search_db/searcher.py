from starstoloves.tasks import search_lastfm
from .query import LastfmQuery


class LastfmSearcher(object):

    def __init__(self, lastfm_app, parser):
        self.lastfm_app = lastfm_app
        self.parser = parser

    def search(self, track_name, artist_name=None):
        # change to take a spotify track, and do the separate searches itself
        # can be a search_or_get
        async_result = search_lastfm.delay(self.lastfm_app, track_name, artist_name)
        return LastfmQuery(async_result.id, self.parser)
