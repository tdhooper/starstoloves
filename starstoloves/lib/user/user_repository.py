from starstoloves.models import User as UserModel
from starstoloves import model_repository
from .user import User

def from_session_key(session_key):
    user_model, created = UserModel.objects.get_or_create(session_key=session_key)
    starred_tracks = user_model.starred_tracks.all() or None
    loved_tracks = user_model.loved_tracks.all() or None
    return User(session_key, starred_tracks, loved_tracks);

def save(user):
    user_model, created = UserModel.objects.get_or_create(session_key=user.session_key)
    if user.starred_tracks:
        user_model.starred_tracks = user.starred_tracks
    if user.loved_tracks:
        user_model.loved_tracks = user.loved_tracks
    user_model.save()

def delete(user):
    try:
        user_model = model_repository.from_user(user)
        user_model.delete()
    except UserModel.DoesNotExist:
        pass;
