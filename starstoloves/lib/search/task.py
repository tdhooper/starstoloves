from __future__ import absolute_import

from celery import shared_task

from starstoloves.lib.lastfm import lastfm_app
from .result import LastfmResultParser


@shared_task
def search_lastfm(track_name, artist_name=None):
    try:
        results = lastfm_app.track.search(track_name, artist_name)
        parser = LastfmResultParser()
        return parser.parse(results)
    except TypeError:
        return None
