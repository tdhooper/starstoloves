from starstoloves.models import LastfmTrack as LastfmTrackModel
from .lastfm_track import LastfmTrack

def get_or_create(url, track_name=None, artist_name=None):
    query = LastfmTrackModel.objects.filter(url=url)
    if query.exists():
        query.update(
            track_name=track_name,
            artist_name=artist_name
        )
    else:
        LastfmTrackModel.objects.create(
            track_name=track_name,
            artist_name=artist_name,
            url=url
        )
    return LastfmTrack(url, track_name, artist_name)

def get_model(track):
    return LastfmTrackModel.objects.get(
        url=track.url,
        track_name=track.track_name,
        artist_name=track.artist_name
    )