from uuid import uuid4

class SearchingTrack:

    def __init__(self, track_name, artist_name, date_saved, searcher, id=None, serialised_queries=None):
        self.track_name = track_name
        self.artist_name = artist_name
        self.date_saved = date_saved
        self.searcher = searcher
        if id is None:
            id = uuid4().hex
        self.id = id
        if serialised_queries is None:
            serialised_queries = {}
        self.serialised_queries = serialised_queries

    @property
    def status(self):
        return self.search['combined'].status

    @property
    def results(self):
        return self.search['combined'].result

    def stop(self):
        self.search['combined'].stop()

    @property
    def search(self):
        if not 'combined' in self.serialised_queries:
            combined_query = self.searcher.search(self.track_name + ' ' + self.artist_name)
            self.serialised_queries['combined'] = combined_query.serialise()
        else:
            combined_query = self.searcher.deserialise(self.serialised_queries['combined'])
        return {
            'combined': combined_query
        }

    def serialise(self):
        return {
            'track_name': self.track_name,
            'artist_name': self.artist_name,
            'date_saved': self.date_saved,
            'id': self.id,
            'serialised_queries': {
                key: query.serialise()
                for key, query in self.search.items()
            },
        }


class SearchingTrackFactory:

    def __init__(self, searcher):
        self.searcher = searcher

    def create(self, track_name, artist_name, date_saved):
        return SearchingTrack(track_name, artist_name, date_saved, self.searcher)

    def deserialise(self, track):
        return SearchingTrack(
            track['track_name'],
            track['artist_name'],
            track['date_saved'],
            self.searcher,
            track['id'],
            track['serialised_queries'],
        )
