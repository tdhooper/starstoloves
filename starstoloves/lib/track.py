class SearchingTrack:

    def __init__(self, track_name, artist_name, date_saved, searcher, search_result_data = None):
        self.track_name = track_name
        self.artist_name = artist_name
        self.date_saved = date_saved
        self.searcher = searcher
        self.search_result_data = search_result_data

    @property
    def search(self):
        if not self.search_result_data:
            search_result = self.searcher.search(self.track_name, self.artist_name)
            self.search_result_data = search_result.data
        elif self.search_result_data['status'] not in ['SUCCESS', 'FAILURE']:
            search_result = self.searcher.result(self.search_result_data['id'])
            self.search_result_data = search_result.data
        return self.search_result_data

    @property
    def data(self):
        return {
            'track_name': self.track_name,
            'artist_name': self.artist_name,
            'date_saved': self.date_saved,
            'search': self.search
        }