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
        results = self.query.results

        if results and self.loved_tracks:

            for result in results:
                result.loved = result in self.loved_tracks

            results = sorted(
                results,
                key=attrgetter('loved'),
                reverse=True
            )

        return results
