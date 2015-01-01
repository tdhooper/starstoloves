import sys

from celery.result import AsyncResult

from starstoloves.models import (
    LastfmSearch as LastfmSearchModel,
    LastfmQuery as LastfmQueryModel,
    LastfmQueryResult as LastfmQueryResultModel,
)
from starstoloves.lib.track import lastfm_track_repository
from starstoloves import model_repository
from .query import LastfmQuery


def get_or_create(track_name, artist_name):
    search_model, created = LastfmSearchModel.objects.select_related('query').get_or_create(track_name=track_name, artist_name=artist_name)
    if search_model.query and search_model.query.task_id is not None:
        async_result = AsyncResult(search_model.query.task_id)
        results = [
            lastfm_track_repository.from_model(track_model)
            for track_model in search_model.query.track_results.all().order_by('lastfmqueryresult')
        ]
    else:
        async_result = None
        results = None
    return LastfmQuery(sys.modules[__name__], track_name, artist_name, async_result, results)


def save(query):
    query_model, created = LastfmQueryModel.objects.get_or_create(task_id=query.async_result.id)
    if query.results:
        for position, track in enumerate(query.results):
            track_model = model_repository.from_lastfm_track(track)
            LastfmQueryResultModel.objects.get_or_create(
                query=query_model,
                track=track_model,
            )
        query_model.save()

    search_model, created = LastfmSearchModel.objects.get_or_create(track_name=query.track_name, artist_name=query.artist_name)
    search_model.query = query_model
    search_model.save()