from starstoloves.tasks import search_lastfm

from celery.result import AsyncResult

class LastfmSearch:

    def __init__(self, lastfm_app):
        self.lastfm_app = lastfm_app

    def search(self, track_name, artist_name):
        async_result = search_lastfm.delay(self.lastfm_app, track_name, artist_name)
        return LastfmSearchResult(async_result.id)

    def result(self, id):
        return LastfmSearchResult(id)

class LastfmSearchResult:

    def __init__(self, id):
        self.async_result = AsyncResult(id)

    def _extract_tracks_from_result(self, result):
        try:
            if isinstance(result['trackmatches'], dict):
                track_results = result['trackmatches']['track']
                if isinstance(track_results, dict):
                    track_results = [track_results]
                tracks = []
                for track in track_results:
                    tracks.append({
                        'track_name': track['name'],
                        'artist_name': track['artist'],
                        'url': track['url'],
                    })
                return tracks
        except TypeError:
            pass

    @property
    def data(self):
        data = {
            'task_id': self.async_result.id,
            'status': self.async_result.status
        }
        if self.async_result.ready():
            tracks = self._extract_tracks_from_result(self.async_result.info)
            if tracks:
                data['tracks'] = tracks
        return data


