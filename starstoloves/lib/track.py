class SearchingTrack:

    def __init__(self, track_name, artist_name, date_saved, searcher, search_query_data = None):
        self.track_name = track_name
        self.artist_name = artist_name
        self.date_saved = date_saved
        self.searcher = searcher
        self.search_query_data = search_query_data

    @property
    def search(self):
        if not self.search_query_data:
            search_query = self.searcher.search(self.track_name, self.artist_name)
            self.search_query_data = search_query.data
        elif self.search_query_data['status'] not in ['SUCCESS', 'FAILURE']:
            search_query = self.searcher.query(self.search_query_data['id'])
            self.search_query_data = search_query.data
        return self.search_query_data

    @property
    def data(self):
        return {
            'track_name': self.track_name,
            'artist_name': self.artist_name,
            'date_saved': self.date_saved,
            'search': self.search
        }