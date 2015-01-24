from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.utils.decorators import decorator_from_middleware

from starstoloves.forms import SpotifyConnectForm
from starstoloves.lib.connection import spotify_connection_repository, lastfm_connection_repository


class ConnectionIndexMiddleware:

    def process_request(self, request):
        lastfm_connection = lastfm_connection_repository.from_user(request.session_user)
        if not lastfm_connection.is_connected:
            return

        spotify_connection = spotify_connection_repository.from_user(request.session_user)
        if request.method == 'POST':
            request.spotify_form = self.spotify_connection_form(spotify_connection, request.POST)
        else:
            request.spotify_form = self.spotify_connection_form(spotify_connection)

        if request.spotify_form.connection_success:
            # Stop double POST on refresh
            return redirect('index')

    def spotify_connection_form(self, spotify_connection, post_data=None):
        if post_data:
            form = SpotifyConnectForm(post_data)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                spotify_connection.connect(username)
                if spotify_connection.state is spotify_connection.FAILED:
                    form.set_connection_error()
                else:
                    form.connection_success = True
            return form
        return SpotifyConnectForm()


connection_index_decorator = decorator_from_middleware(ConnectionIndexMiddleware)


class ConnectionStatusMiddleware:

    def process_request(self, request):
        lastfm_connection = lastfm_connection_repository.from_user(request.session_user)
        spotify_connection = spotify_connection_repository.from_user(request.session_user)

        request.is_lastfm_connected = lambda: lastfm_connection.is_connected
        request.is_spotify_connected = lambda: spotify_connection.is_connected


connection_status_decorator = decorator_from_middleware(ConnectionStatusMiddleware)


def connection_index_processor(request):
    context = {}
    add_lastfm_context(request, context)
    lastfm_connection = lastfm_connection_repository.from_user(request.session_user)
    if lastfm_connection.is_connected:
        add_spotify_context(request, context)
    return context


def add_lastfm_context(request, context):
    lastfm_connection = lastfm_connection_repository.from_user(request.session_user)
    if lastfm_connection.is_connected:
        context.update({
            'lfmUsername': lastfm_connection.username,
            'lfmDisconnectUrl': reverse('disconnect_lastfm'),
        })
    else:
        context.update({
            'lfmConnectUrl': reverse('connect_lastfm'),
        })
    if lastfm_connection.state is lastfm_connection.FAILED:
        context.update({
            'lfmConnectFailure': True
        })


def add_spotify_context(request, context):
    spotify_connection = spotify_connection_repository.from_user(request.session_user)
    if spotify_connection.is_connected:
        context.update({
            'spUsername': spotify_connection.username,
            'spDisconnectUrl': reverse('disconnect_spotify'),
        })
    else:
        context.update({
            'spConnectUrl': reverse('connect_spotify'),
        })
    if spotify_connection.state is spotify_connection.FAILED:
        context.update({
            'spConnectFailure': True
        })


def connect_lastfm(request):
    lastfm_connection = lastfm_connection_repository.from_user(request.session_user)
    if lastfm_connection.is_connected:
        return redirect('index')
    token = request.GET.get('token')
    if token:
        lastfm_connection.connect(token)
        return redirect('index')
    callback_url = request.build_absolute_uri(reverse('connect_lastfm'))
    auth_url = lastfm_connection.auth_url(callback_url)
    return redirect(auth_url)


def connect_spotify(request):
    spotify_connection = spotify_connection_repository.from_user(request.session_user)
    if spotify_connection.is_connected:
        return redirect('index')
    code = request.GET.get('code')
    callback_url = request.build_absolute_uri(reverse('connect_spotify'))
    if code:
        spotify_connection.connect(code, callback_url)
        return redirect('index')
    auth_url = spotify_connection.auth_url(callback_url)
    return redirect(auth_url)


def disconnect_lastfm(request):
    lastfm_connection = lastfm_connection_repository.from_user(request.session_user)
    lastfm_connection.disconnect()
    return redirect('index')


def disconnect_spotify(request):
    spotify_connection = spotify_connection_repository.from_user(request.session_user)
    spotify_connection.disconnect()
    return redirect('index')
