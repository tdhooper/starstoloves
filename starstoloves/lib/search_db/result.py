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

        tracks = [{
            'track_name': track['name'],
            'artist_name': track['artist'],
            'url': track['url'],
        } for track in track_results]

        return tracks


class LastfmResultParserWithLoves(LastfmResultParser):

    def __init__(self, loved_tracks_urls):
        self.loved_tracks_urls = loved_tracks_urls

    def parse(self, result):
        tracks = super().parse(result)
        if isinstance(tracks, list):
            for track in tracks:
                track['loved'] = track['url'] in self.loved_tracks_urls
        return tracks
