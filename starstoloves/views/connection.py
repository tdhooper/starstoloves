from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.utils.decorators import decorator_from_middleware

from starstoloves.forms import SpotifyConnectForm
from starstoloves.lib.user.spotify_user import SpotifyUser
from starstoloves.lib.user.lastfm_user import LastfmUser


class ConnectionMiddleware:

    def process_request(self, request):
        lastfm_user = LastfmUser(request.session_user)
        if not lastfm_user.connection.is_connected:
            return

        spotify_user = SpotifyUser(request.session_user)
        if request.method == 'POST':
            request.spotify_form = self.spotify_connection_form(spotify_user.connection, request.POST)
        else:
            request.spotify_form = self.spotify_connection_form(spotify_user.connection)

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


connection_index_decorator = decorator_from_middleware(ConnectionMiddleware)


def connection_index_processor(request):
    context = {}
    add_lastfm_context(request, context)
    lastfm_user = LastfmUser(request.session_user)
    if lastfm_user.connection.is_connected:
        add_spotify_context(request, context)
    return context


def add_lastfm_context(request, context):
    lastfm_user = LastfmUser(request.session_user)
    if lastfm_user.connection.is_connected:
        context.update({
            'lfmUsername': lastfm_user.connection.username,
            'lfmDisconnectUrl': reverse('disconnect_lastfm'),
        })
    else:
        context.update({
            'lfmConnectUrl': reverse('connect_lastfm'),
        })
    if lastfm_user.connection.state is lastfm_user.connection.FAILED:
        context.update({
            'lfmConnectFailure': True
        })


def add_spotify_context(request, context):
    spotify_user = SpotifyUser(request.session_user)
    if spotify_user.connection.is_connected:
        context.update({
            'spUsername': spotify_user.connection.username,
            'spDisconnectUrl': reverse('disconnect_spotify'),
        })
    else:
        context.update({
            'spForm': request.spotify_form,
            'spConnectUrl': reverse('index'),
        })


def connect_lastfm(request):
    lastfm_user = LastfmUser(request.session_user)
    if lastfm_user.connection.is_connected:
        return redirect('index')
    token = request.GET.get('token')
    if token:
        lastfm_user.connection.connect(token)
        return redirect('index')
    callback_url = request.build_absolute_uri(reverse('connect_lastfm'))
    auth_url = lastfm_user.connection.auth_url(callback_url)
    return redirect(auth_url)


def disconnect_lastfm(request):
    lastfm_user = LastfmUser(request.session_user)
    lastfm_user.connection.disconnect()
    return redirect('index')


def disconnect_spotify(request):
    spotify_user = SpotifyUser(request.session_user)
    spotify_user.connection.disconnect()
    return redirect('index')
