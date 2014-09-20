from starstoloves.lib.search.searcher import LastfmSearcher


def starred_track_searches(sp_user):
    searcher = LastfmSearcher()
    searches = [
        {
            'track': track,
            'query': searcher.search(track),
        }
        for track in sp_user.starred_tracks
    ]
    return searches


class User():

    def __init__(self, session_key, starred_tracks=None, loved_tracks=None):
        self.session_key = session_key
        self.starred_tracks = starred_tracks
        self.loved_tracks = loved_tracks