class SearchingTrack:

    def __init__(self, track_name, artist_name, date_saved, searcher, serialised_query=None):
        self.track_name = track_name
        self.artist_name = artist_name
        self.date_saved = date_saved
        self.searcher = searcher
        self.serialised_query = serialised_query

    @property
    def search(self):
        if not self.serialised_query:
            query = self.searcher.search(self.track_name, self.artist_name)
            self.serialised_query = query.serialise()
        else:
            query = self.searcher.deserialise(self.serialised_query)
        return query

    @property
    def data(self):
        return {
            'track_name': self.track_name,
            'artist_name': self.artist_name,
            'date_saved': self.date_saved,
            'search': self.search.data,
        }

    def serialise(self):
        return {
            'track_name': self.track_name,
            'artist_name': self.artist_name,
            'date_saved': self.date_saved,
            'serialised_query': self.search.serialise(),
        }

