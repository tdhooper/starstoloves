from starstoloves.models import User as UserModel
from starstoloves import model_repository
from starstoloves.lib.track import lastfm_track_repository
from .user import User

def from_session_key(session_key):
    user_model, created = UserModel.objects.get_or_create(session_key=session_key)
    if user_model.loved_tracks.exists():
        loved_tracks = [
            lastfm_track_repository.from_model(track_model)
            for track_model in user_model.loved_tracks.all()
        ]
    else:
        loved_tracks = None
    return User(session_key, loved_tracks);

def save(user):
    user_model, created = UserModel.objects.get_or_create(session_key=user.session_key)
    if user.loved_tracks:
        user_model.loved_tracks = [
            model_repository.from_lastfm_track(track)
            for track in user.loved_tracks
        ]
    user_model.save()

def delete(user):
    try:
        user_model = model_repository.from_user(user)
        user_model.delete()
    except UserModel.DoesNotExist:
        pass;
