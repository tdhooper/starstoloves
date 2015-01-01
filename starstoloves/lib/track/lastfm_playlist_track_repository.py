from starstoloves.models import LastfmPlaylistTrack as LastfmPlaylistTrackModel
from starstoloves import model_repository
from .lastfm_track import LastfmPlaylistTrack, LastfmTrack
from . import lastfm_track_repository


def get_or_create(user, url, added, track_name=None, artist_name=None, listeners=None):
    track = lastfm_track_repository.get_or_create(
        url=url,
        track_name=track_name,
        artist_name=artist_name,
        listeners=listeners,
    )
    LastfmPlaylistTrackModel.objects.get_or_create(
        user=model_repository.from_user(user),
        track=model_repository.from_lastfm_track(track),
        added=added
    )
    return LastfmPlaylistTrack(
        user=user,
        url=url,
        track_name=track_name,
        artist_name=artist_name,
        listeners=listeners,
        added=added,
    )


def for_user(user):
    return [
        LastfmPlaylistTrack(
            user=user,
            url=model.track.url,
            track_name=model.track.track_name,
            artist_name=model.track.artist_name,
            listeners=model.track.listeners,
            added=model.added
        )
        for model in LastfmPlaylistTrackModel.objects.filter(
            user=model_repository.from_user(user)
        )
    ]


def clear_user(user):
    LastfmPlaylistTrackModel.objects.filter(
        user=model_repository.from_user(user)
    ).delete()
