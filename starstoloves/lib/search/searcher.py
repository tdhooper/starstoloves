from starstoloves.tasks import search_lastfm
from starstoloves.models import LastfmSearch
from .query import LastfmQuery

class LastfmSearcher(object):

    def search(self, track):
        search, created = LastfmSearch.objects.get_or_create(track_name=track['track_name'], artist_name=track['artist_name'])
        if created:
            async_result = search_lastfm.delay(track['track_name'], track['artist_name'])
            query = LastfmQuery(async_result.id)
            search.query = query.query_model
            search.save()
            return query
        else:
            query = LastfmQuery(search.query.task_id)
        return query
