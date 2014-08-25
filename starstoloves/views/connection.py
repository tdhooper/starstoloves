from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.utils.decorators import decorator_from_middleware

from starstoloves.forms import SpotifyConnectForm


class ConnectionMiddleware:

    def process_request(self, request):
        if not request.lastfm_connection.is_connected():
            return

        if request.method == 'POST':
            request.spotify_form = self.spotify_connection_form(request.spotify_connection, request.POST)
        else:
            request.spotify_form = self.spotify_connection_form(request.spotify_connection)

        if request.spotify_form.connection_success:
            # Stop double POST on refresh
            return redirect('index')

    def spotify_connection_form(self, spotify_connection, post_data=None):
        if post_data:
            form = SpotifyConnectForm(post_data)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                spotify_connection.connect(username)
                if spotify_connection.get_connection_state() is spotify_connection.FAILED:
                    form.set_connection_error()
                else:
                    form.connection_success = True
            return form
        return SpotifyConnectForm()


connection_index_decorator = decorator_from_middleware(ConnectionMiddleware)


def connection_index_processor(request):
    context = {}
    add_lastfm_context(request, context)
    if request.lastfm_connection.is_connected():
        add_spotify_context(request, context)
    return context


def add_lastfm_context(request, context):
    if request.lastfm_connection.is_connected():
        context.update({
            'lfmUsername': request.lastfm_connection.get_username(),
            'lfmDisconnectUrl': reverse('disconnect_lastfm'),
        })
    else:
        context.update({
            'lfmConnectUrl': reverse('connect_lastfm'),
        })
    if request.lastfm_connection.get_connection_state() is request.lastfm_connection.FAILED:
        context.update({
            'lfmConnectFailure': True
        })


def add_spotify_context(request, context):
    if request.spotify_connection.is_connected():
        context.update({
            'spUsername': request.spotify_connection.get_username(),
            'spDisconnectUrl': reverse('disconnect_spotify'),
        })
    else:
        context.update({
            'spForm': request.spotify_form,
            'spConnectUrl': reverse('index'),
        })


def connect_lastfm(request):
    if request.lastfm_connection.is_connected():
        return redirect('index')
    token = request.GET.get('token')
    if token:
        request.lastfm_connection.connect(token)
        return redirect('index')
    callback_url = request.build_absolute_uri(reverse('connect_lastfm'))
    auth_url = request.lastfm_connection.get_auth_url(callback_url)
    return redirect(auth_url)


def disconnect_lastfm(request):
    request.lastfm_connection.disconnect()
    return redirect('index')


def disconnect_spotify(request):
    request.spotify_connection.disconnect()
    return redirect('index')
