from starstoloves.tasks import search_lastfm

from celery.result import AsyncResult
from celery.task.control import revoke

class LastfmSearch(object):

    def __init__(self, lastfm_app):
        self.lastfm_app = lastfm_app

    def search(self, track_name, artist_name=None):
        async_result = search_lastfm.delay(self.lastfm_app, track_name, artist_name)
        return self.factory_result(async_result.id)

    def deserialise(self, query):
        return LastfmSearchQuery(query['id'], query['status'], query['result'])

    def factory_result(self, id):
        return LastfmSearchQuery(id)    


class LastfmSearchQuery(object):

    def __init__(self, id, status=None, result=None):
        self.id = id
        if status in ['SUCCESS', 'FAILURE']:
            self._status = status
            self._result = result
        else:
            self.async_result = AsyncResult(id)

    def stop(self):
        revoke(self.id)

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
    def status(self):
        if hasattr(self, '_status'):
            return self._status
        return self.async_result.status

    @property
    def result(self):
        if hasattr(self, '_result'):
            return self._result
        if self.async_result.ready():
            return self._extract_tracks_from_result(self.async_result.info)

    def serialise(self):
        return {
            'id': self.id,
            'status': self.status,
            'result': self.result,
        }


class LastfmSearchWithLoves(LastfmSearch):

    def __init__(self, lastfm_app, loved_tracks_urls):
        super(LastfmSearchWithLoves, self).__init__(lastfm_app)
        self.loved_tracks_urls = loved_tracks_urls

    def factory_query(self, id):
        return LastfmSearchQueryWithLoves(id, self.loved_tracks_urls)


class LastfmSearchQueryWithLoves(LastfmSearchQuery):

    def __init__(self, id, loved_tracks_urls):
        super(LastfmSearchQueryWithLoves, self).__init__(id)
        self.loved_tracks_urls = loved_tracks_urls

    def _extract_tracks_from_result(self, result):
        tracks = super(LastfmSearchQueryWithLoves, self)._extract_tracks_from_result(result)
        if isinstance(tracks, list):
            for track in tracks:
                track['loved'] = track['url'] in self.loved_tracks_urls
        return tracks



