from . import query_repository

class LastfmSearcher(object):

    def search(self, track):
        return query_repository.get_or_create(track.track_name, track.artist_name)
