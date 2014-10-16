from starstoloves.models import SpotifyTrack as SpotifyTrackModel
from .spotify_track import SpotifyTrack

def get_or_create(track_name, artist_name):
    SpotifyTrackModel.objects.get_or_create(track_name=track_name, artist_name=artist_name)
    return SpotifyTrack(track_name, artist_name)
