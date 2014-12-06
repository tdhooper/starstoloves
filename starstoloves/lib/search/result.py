from starstoloves.lib.track.lastfm_track import LastfmTrack


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
            LastfmTrack(
                url=track['url'],
                track_name=track['name'],
                artist_name=track['artist'],
                listeners=track['listeners'],
            )
            for track in track_results
        ]

        return tracks
