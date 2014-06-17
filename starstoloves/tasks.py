from __future__ import absolute_import

from celery import shared_task

@shared_task
def search_lastfm(lastfm_app, track_name, artist_name):
    return lastfm_app.track.search(artist_name + ' ' + track_name)