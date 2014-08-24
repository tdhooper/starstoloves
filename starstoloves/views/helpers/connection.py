from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from starstoloves.forms import SpotifyConnectForm

class ConnectionHelper:

    _is_connected = False
    stop_double_post_on_refresh = False

    def __init__(self, lastfm_connection, spotify_connection):
        self.lastfm_connection = lastfm_connection
        self.spotify_connection = spotify_connection

    def index(self, request):
        context = {}

        self.lastfm_steps(context)
        if not self.lastfm_connection.is_connected():
            return (None, context)

        self.spotify_steps(context, request)
        if not self.spotify_connection.is_connected():
            return (None, context)

        if self.stop_double_post_on_refresh:
            return (redirect('index'), context)

        self._is_connected = True
        return (None, context)

    @property
    def is_connected(self):
        return self._is_connected

    def lastfm_steps(self, context):
        self.add_lastfm_context(context)

    def spotify_steps(self, context, request):
        if request.method == 'POST':
            form = self.spotify_connection_form(request.POST)
        else:
            form = self.spotify_connection_form()

        if form.connection_success:
            self.stop_double_post_on_refresh = True

        self.add_spotify_context(context, form)

    def spotify_connection_form(self, post_data=None):
        if post_data:
            form = SpotifyConnectForm(post_data)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                self.spotify_connection.connect(username)
                if self.spotify_connection.get_connection_state() is self.spotify_connection.FAILED:
                    form.set_connection_error()
                else:
                    form.connection_success = True
            return form
        return SpotifyConnectForm()

    def add_lastfm_context(self, context):
        if self.lastfm_connection.is_connected():
            context.update({
                'lfmUsername': self.lastfm_connection.get_username(),
                'lfmDisconnectUrl': reverse('disconnect_lastfm'),
            })
        else:
            context.update({
                'lfmConnectUrl': reverse('connect_lastfm'),
            })
        if self.lastfm_connection.get_connection_state() is self.lastfm_connection.FAILED:
            context.update({
                'lfmConnectFailure': True
            })

    def add_spotify_context(self, context, form):
        if self.spotify_connection.is_connected():
            context.update({
                'spUsername': self.spotify_connection.get_username(),
                'spDisconnectUrl': reverse('disconnect_spotify'),
            })
        else:
            context.update({
                'spForm': form,
                'spConnectUrl': reverse('index'),
            })

    def connect_lastfm(self, request):
        if self.lastfm_connection.is_connected():
            return redirect('index')
        token = request.GET.get('token')
        if token:
            self.lastfm_connection.connect(token)
            return redirect('index')
        callback_url = request.build_absolute_uri(reverse('connect_lastfm'))
        auth_url = self.lastfm_connection.get_auth_url(callback_url)
        return redirect(auth_url)

    def disconnect_lastfm(self):
        self.lastfm_connection.disconnect()
        return redirect('index')

    def disconnect_spotify(self):
        self.spotify_connection.disconnect()
        return redirect('index')
