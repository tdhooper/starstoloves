from django import forms
import spotify

class SpotifyConnectForm(forms.Form):

    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))

    def __init__(self, *args, **kwargs):
        self.spotifySession =  kwargs.pop('spotifySession', None)
        super(SpotifyConnectForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(SpotifyConnectForm, self).clean()
        username = cleaned_data.get('username')
        userUri = 'spotify:user:' + username

        # for now the only way I know of validating a user exists is to try and load a playlist
        if username:
            user = self.spotifySession.get_user(userUri)
            starred = user.load().starred
            try:
                tracks = starred.load().tracks_with_metadata
            except spotify.Error:
                raise forms.ValidationError('User not found')

            cleaned_data['userUri'] = userUri

        return cleaned_data