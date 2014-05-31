from django import forms
from django.forms.util import ErrorList

class SpotifyConnectForm(forms.Form):

    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))

    connection_success = False

    def set_connection_error(self):
        errorList = ErrorList()
        errorList.append('User not found')
        self._errors = {
            'username': errorList
        }        