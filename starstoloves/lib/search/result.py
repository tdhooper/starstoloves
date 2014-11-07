from starstoloves.lib.track import lastfm_track_repository


class LastfmResultParser(object):

    def parse(self, result):
        if not isinstance(result, dict):
            return None

        matches = result.get('trackmatches')
        if not isinstance(matches, dict):
            return None

        track_results = matches.get('track')
        if isinstance(track_results, dict):
            track_results = [track_results]

        tracks = [
            lastfm_track_repository.get_or_create(
                url=track['url'],
                track_name=track['name'],
                artist_name=track['artist']
            )
            for track in track_results
        ]

        return tracks
