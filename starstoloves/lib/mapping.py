from operator import attrgetter

from starstoloves.lib.search import query_repository


class TrackMapping():


    def __init__(self, track, loved_tracks=None):
        self.track = track
        self.loved_tracks = loved_tracks
        self.query = query_repository.get_or_create(track.track_name, track.artist_name)


    @property
    def id(self):
        return self.query.id


    @property
    def status(self):
        return self.query.status


    @property
    def results(self):
        tracks = self.query.results

        if not tracks:
            return None

        results = [
            {
                'track': track,
                'loved': False,
            }
            for track in tracks
        ]

        if self.loved_tracks:

            for result in results:
                result['loved'] = next((
                    loved_track.added
                    for loved_track in self.loved_tracks
                    if loved_track.url == result['track'].url
                ), False)

            results = sorted(results, key=lambda result: 0 if result['loved'] else 1)

        return results
