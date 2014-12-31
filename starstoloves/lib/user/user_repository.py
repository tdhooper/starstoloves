import sys

from starstoloves.models import User as UserModel
from starstoloves import model_repository
from starstoloves.lib.track import lastfm_track_repository
from .user import User

def from_session_key(session_key):
    user_model, created = UserModel.objects.get_or_create(session_key=session_key)
    return User(
        session_key=session_key,
        repository=sys.modules[__name__],
    );


def delete(user):
    try:
        user_model = model_repository.from_user(user)
        user_model.delete()
    except UserModel.DoesNotExist:
        pass;
