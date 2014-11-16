from starstoloves.models import LastfmTrack as LastfmTrackModel
from .lastfm_track import LastfmTrack


def get_or_create(url, track_name=None, artist_name=None, listeners=None):
    track = LastfmTrack(url, track_name, artist_name, listeners)
    save(track)
    return track


def from_model(model):
    return LastfmTrack(
        url=model.url,
        track_name=model.track_name,
        artist_name=model.artist_name,
        listeners=model.listeners,
    )


def save(track):
    query = LastfmTrackModel.objects.filter(url=track.url)
    if query.exists():
        query.update(
            track_name=track.track_name,
            artist_name=track.artist_name,
            listeners=track.listeners,
        )
    else:
        LastfmTrackModel.objects.create(
            track_name=track.track_name,
            artist_name=track.artist_name,
            url=track.url,
            listeners=track.listeners,
        )
