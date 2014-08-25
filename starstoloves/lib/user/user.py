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
