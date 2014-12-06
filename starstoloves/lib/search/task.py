from __future__ import absolute_import

from celery import shared_task

from .multi import multi_search


@shared_task
def search_lastfm(track_name, artist_name):
    return multi_search(track_name, artist_name)