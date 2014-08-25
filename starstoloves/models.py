from django.db import models

class LastfmTrack(models.Model):
    track_name = models.CharField(max_length=3000, null=True)
    artist_name = models.CharField(max_length=3000, null=True)
    url = models.URLField(max_length=3000)

class SpotifyTrack(models.Model):
    track_name = models.CharField(max_length=3000, null=True)
    artist_name = models.CharField(max_length=3000, null=True)

class User(models.Model):
    session_key = models.CharField(max_length=300)
    starred_tracks = models.ManyToManyField(SpotifyTrack, null=True)
    loved_tracks = models.ManyToManyField(LastfmTrack, null=True)

class LastfmConnection(models.Model):
    username = models.CharField(max_length=300, null=True)
    state = models.IntegerField(null=True)
    user = models.OneToOneField(User, related_name='lastfm_connection')

class SpotifyConnection(models.Model):
    username = models.CharField(max_length=300, null=True)
    user_uri = models.CharField(max_length=300, null=True)
    state = models.IntegerField(null=True)
    user = models.OneToOneField(User, related_name='spotify_connection')

class LastfmQuery(models.Model):
    task_id = models.CharField(max_length=300)
    track_results = models.ManyToManyField(LastfmTrack, null=True)

class LastfmSearch(models.Model):
    track_name = models.CharField(max_length=300, null=True)
    artist_name = models.CharField(max_length=300, null=True)
    query = models.OneToOneField(LastfmQuery, related_name='search', null=True)
