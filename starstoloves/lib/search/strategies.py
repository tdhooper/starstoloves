from starstoloves.lib.lastfm import lastfm_app
from .result import LastfmResultParser


def search_strategy(strategy):
    def call_and_parse(*args):
        try:
            parser = LastfmResultParser()
            results = strategy(*args)
            return parser.parse(results)
        except TypeError:
            return None
    return call_and_parse


@search_strategy
def separate_search_strategy(track_name, artist_name):
    return lastfm_app.track.search(track_name, artist_name)


@search_strategy
def combined_search_strategy(track_name, artist_name):
    return lastfm_app.track.search(' '.join([track_name, artist_name]))