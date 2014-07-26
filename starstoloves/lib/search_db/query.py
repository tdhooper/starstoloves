from celery.result import AsyncResult
from celery.task.control import revoke

from starstoloves.models import LastfmQuery as LastfmQueryModel
from starstoloves.models import LastfmTrack as LastfmTrackModel


class LastfmQuery(object):

    def __init__(self, id, parser):
        self.id = id
        self.async_result = AsyncResult(id)
        self.parser = parser

    @property
    def status(self):
        return self.async_result.status

    @property
    def response_data(self):
        if self.async_result.ready():
            return self.async_result.info

    @property
    def results(self):
        if self.response_data:
            parsed = self.parser.parse(self.response_data)
            return parsed

    def stop(self):
        revoke(self.id)


class LastfmCachingQuery(LastfmQuery):

    def __init__(self, id, parser):
        super().__init__(id, parser)
        self.query_model, created = LastfmQueryModel.objects.get_or_create(task_id=id)
        self.query_model.save()

    def _store_tracks(self, tracks):
        track_models = [
            LastfmTrackModel.objects.get_or_create(
                track_name=track['track_name'],
                artist_name=track['artist_name'],
                url=track['url']
            )[0]
            for track in tracks
        ]
        self.query_model.track_results.add(*track_models)

    def _retrieve_tracks(self):
        track_models = self.query_model.track_results.all()
        if track_models:
            return track_models.values('track_name', 'artist_name', 'url')

    @property
    def results(self):
        stored_tracks = self._retrieve_tracks()
        if stored_tracks:
            return stored_tracks

        tracks = super().results
        if isinstance(tracks, list):
            self._store_tracks(tracks)

        return tracks
