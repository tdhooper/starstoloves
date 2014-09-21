import sys

from starstoloves.lib.spotify_session import session as spotify_session
from starstoloves.models import SpotifyConnection, User
from .spotify_connection import SpotifyConnectionHelper

def from_user(user):
    user_model = User.objects.get(session_key=user.session_key)
    connection_model, created = SpotifyConnection.objects.get_or_create(user=user_model)
    return SpotifyConnectionHelper(
        user,
        spotify_session,
        username=connection_model.username,
        state=connection_model.state,
        user_uri=connection_model.user_uri,
        repository=sys.modules[__name__]
    )

def save(connection):
    user_model = User.objects.get(session_key=connection.user.session_key)
    connection_model, created = SpotifyConnection.objects.get_or_create(user=user_model)
    connection_model.username = connection.username
    connection_model.state = connection.state
    connection_model.user_uri = connection.user_uri
    connection_model.save()

def delete(connection):
    user_model = User.objects.get(session_key=connection.user.session_key)
    try:
        connection_model = SpotifyConnection.objects.get(user=user_model)
        connection_model.delete()
    except SpotifyConnection.DoesNotExist:
        pass;
