from starstoloves.models import SpotifyTrack

class SpotifyUser:

    def __init__(self, user, spotify_session, spotify_connection):
        self.spotify_session = spotify_session
        self.spotify_connection = spotify_connection
        self.user = user

    @property
    def starred_tracks(self):
        tracks = self._starred_tracks_data
        track_models = [
            SpotifyTrack.objects.get_or_create(
                track_name=track['track_name'],
                artist_name=track['artist_name'],
            )[0]
            for track in tracks
        ]
        self.user.starred_tracks.add(*track_models)
        return tracks

    @property
    def _starred_tracks_data(self):
        starred = self.api_user.starred
        playlist = starred.load().tracks_with_metadata
        tracks = [(item, item.track.load()) for item in playlist]
        track_data = [
            {
                'track_name': track.name,
                'artist_name': track.artists[0].load().name,
                'date_saved': item.create_time,
            }
            for item, track in tracks
        ]
        return track_data

    @property
    def api_user(self):
        user_uri = self.spotify_connection.get_user_uri()
        return self.spotify_session.get_user(user_uri).load()
