from __future__ import absolute_import

from celery import shared_task

from starstoloves.lib.lastfm import lastfm_app

@shared_task
def search_lastfm(track_name, artist_name=None):
    return lastfm_app.track.search(track_name, artist_name)