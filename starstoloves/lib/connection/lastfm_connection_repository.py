import sys

from starstoloves.lib.lastfm import lastfm_app
from starstoloves.models import LastfmConnection, User
from .lastfm_connection import LastfmConnectionHelper

def from_user(user):
    user_model = User.objects.get(session_key=user.session_key)
    connection_model, created = LastfmConnection.objects.get_or_create(user=user_model)
    return LastfmConnectionHelper(
        user,
        lastfm_app,
        username=connection_model.username,
        state=connection_model.state,
        repository=sys.modules[__name__]
    )

def save(connection):
    user_model = User.objects.get(session_key=connection.user.session_key)
    connection_model, created = LastfmConnection.objects.get_or_create(user=user_model)
    connection_model.username = connection.username
    connection_model.state = connection.state
    connection_model.save()

def delete(connection):
    user_model = User.objects.get(session_key=connection.user.session_key)
    try:
        connection_model = LastfmConnection.objects.get(user=user_model)
        connection_model.delete()
    except LastfmConnection.DoesNotExist:
        pass;
