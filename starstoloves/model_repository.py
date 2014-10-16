from starstoloves.models import User, SpotifyTrack, LastfmTrack


def from_user(user):
    return User.objects.get(
        session_key=user.session_key
    )


def from_spotify_track(track):
    return SpotifyTrack.objects.get(
        track_name=track.track_name,
        artist_name=track.artist_name
    )


def from_lastfm_track(track):
    return LastfmTrack.objects.get(
        url=track.url,
        track_name=track.track_name,
        artist_name=track.artist_name
    )
