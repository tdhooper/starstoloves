from starstoloves.models import SpotifyPlaylistTrack as SpotifyPlaylistTrackModel
from starstoloves import model_repository
from .spotify_track import SpotifyPlaylistTrack, SpotifyTrack
from . import spotify_track_repository


def get_or_create(user, track_name, artist_name, added):
    track = spotify_track_repository.get_or_create(
        track_name=track_name,
        artist_name=artist_name
    )
    SpotifyPlaylistTrackModel.objects.get_or_create(
        user=model_repository.from_user(user),
        track=model_repository.from_spotify_track(track),
        added=added
    )
    return SpotifyPlaylistTrack(user, track_name, artist_name, added)


def for_user(user):
    return [
        SpotifyPlaylistTrack(
            user=user,
            track_name=model.track.track_name,
            artist_name=model.track.artist_name,
            added=model.added
        )
        for model in SpotifyPlaylistTrackModel.objects.filter(
            user=model_repository.from_user(user)
        )
    ]
