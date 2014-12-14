import sys

from starstoloves.lib.lastfm import lastfm_app
from starstoloves import model_repository
from starstoloves.models import LastfmConnection, User
from .lastfm_connection import LastfmConnectionHelper

def from_user(user):
    user_model = model_repository.from_user(user)
    connection_model, created = LastfmConnection.objects.get_or_create(user=user_model)
    return LastfmConnectionHelper(
        user,
        lastfm_app,
        username=connection_model.username,
        session_key=connection_model.session_key,
        state=connection_model.state,
        repository=sys.modules[__name__]
    )

def save(connection):
    user_model = model_repository.from_user(connection.user)
    connection_model, created = LastfmConnection.objects.get_or_create(user=user_model)
    connection_model.username = connection.username
    connection_model.session_key = connection.session_key
    connection_model.state = connection.state
    connection_model.save()

def delete(connection):
    user_model = model_repository.from_user(connection.user)
    try:
        connection_model = LastfmConnection.objects.get(user=user_model)
        connection_model.delete()
    except LastfmConnection.DoesNotExist:
        pass;
