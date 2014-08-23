from starstoloves.lib.search_db.searcher import LastfmSearcher

def starred_track_searches(sp_user, lastfm_app):
    searcher = LastfmSearcher(lastfm_app)
    searches = [
        {
            'track': track,
            'query': searcher.search(track),
        }
        for track in sp_user.starred_tracks
    ]
    return searches
