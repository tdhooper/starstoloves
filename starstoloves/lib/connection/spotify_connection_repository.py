import sys

from starstoloves import model_repository
from starstoloves.models import SpotifyConnection, User
from .spotify_connection import SpotifyConnectionHelper

def from_user(user):
    user_model = model_repository.from_user(user)
    connection_model, created = SpotifyConnection.objects.get_or_create(user=user_model)
    return SpotifyConnectionHelper(
        user,
        username=connection_model.username,
        state=connection_model.state,
        token=connection_model.token,
        repository=sys.modules[__name__]
    )

def save(connection):
    user_model = model_repository.from_user(connection.user)
    connection_model, created = SpotifyConnection.objects.get_or_create(user=user_model)
    connection_model.username = connection.username
    connection_model.state = connection.state
    connection_model.token = connection.token
    connection_model.save()

def delete(connection):
    user_model = model_repository.from_user(connection.user)
    try:
        connection_model = SpotifyConnection.objects.get(user=user_model)
        connection_model.delete()
    except SpotifyConnection.DoesNotExist:
        pass;
