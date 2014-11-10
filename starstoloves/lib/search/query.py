from celery.task.control import revoke

from .task import search_lastfm
from starstoloves.lib.track import lastfm_track_repository


class LastfmQuery(object):


    def __init__(
        self,
        repository,
        track_name,
        artist_name=None,
        async_result=None,
        results=None
    ):
        self.repository = repository
        self.track_name = track_name
        self.artist_name = artist_name
        self._async_result = async_result
        self._results = results


    @property
    def async_result(self):
        if not self._async_result:
            self._async_result = search_lastfm.delay(self.track_name, self.artist_name)
            self.repository.save(self)
        return self._async_result


    @property
    def status(self):
        return self.async_result.status


    @property
    def id(self):
        return self.async_result.id


    @property
    def response_data(self):
        if self.async_result.ready():
            return self.async_result.info


    @property
    def results(self):
        if not self._results and self.response_data:
            self._results = self.response_data
            for track in self._results:
                lastfm_track_repository.save(track)
            if self._results:
                self.repository.save(self)
        return self._results


    def stop(self):
        revoke(self.async_result.id)
