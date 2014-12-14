from starstoloves.models import LastfmTrack as LastfmTrackModel
from .lastfm_track import LastfmTrack


def get_or_create(url, track_name=None, artist_name=None, listeners=None):
    try:
        model = LastfmTrackModel.objects.get(url=url)
    except LastfmTrackModel.DoesNotExist:
        model = LastfmTrackModel.objects.create(
            url=url,
            track_name=track_name,
            artist_name=artist_name,
            listeners=listeners,
        )
    return from_model(model)


def from_model(model):
    return LastfmTrack(
        url=model.url,
        track_name=model.track_name,
        artist_name=model.artist_name,
        listeners=model.listeners,
    )


def save(track):
    get_or_create(track.url, track.track_name, track.artist_name, track.listeners)


def get(url):
    try:
        model = LastfmTrackModel.objects.get(url=url)
        return from_model(model)
    except LastfmTrackModel.DoesNotExist:
        return None
