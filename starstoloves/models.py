from django.db import models

class User(models.Model):
    session_key = models.CharField(max_length=300)

class LastfmConnection(models.Model):
    username = models.CharField(max_length=300, null=True)
    state = models.IntegerField(null=True)
    user = models.OneToOneField(User, related_name='lastfm_connection')

class SpotifyConnection(models.Model):
    username = models.CharField(max_length=300, null=True)
    user_uri = models.CharField(max_length=300, null=True)
    state = models.IntegerField(null=True)
    user = models.OneToOneField(User, related_name='spotify_connection')

class LastfmTrack(models.Model):
    track_name = models.CharField(max_length=300, null=True)
    artist_name = models.CharField(max_length=300, null=True)
    url = models.URLField()

class LastfmQuery(models.Model):
    task_id = models.CharField(max_length=300)
    track_results = models.ManyToManyField(LastfmTrack, null=True)
