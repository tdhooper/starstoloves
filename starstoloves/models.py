from django.db import models


class LastfmTrack(models.Model):
    track_name = models.CharField(max_length=3000, null=True)
    artist_name = models.CharField(max_length=3000, null=True)
    url = models.URLField(max_length=3000, unique=True)
    listeners = models.IntegerField(null=True)


class SpotifyTrack(models.Model):
    track_name = models.CharField(max_length=3000, null=True)
    artist_name = models.CharField(max_length=3000, null=True)


class User(models.Model):
    session_key = models.CharField(max_length=300)
    starred_tracks = models.ManyToManyField(SpotifyTrack, null=True, through='SpotifyPlaylistTrack')
    loved_tracks = models.ManyToManyField(LastfmTrack, null=True, through='LastfmPlaylistTrack')


class SpotifyPlaylistTrack(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey(SpotifyTrack, on_delete=models.CASCADE)
    added = models.DateTimeField()


class LastfmPlaylistTrack(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey(LastfmTrack, on_delete=models.CASCADE)
    added = models.DateTimeField()


class LastfmConnection(models.Model):
    username = models.CharField(max_length=300, null=True)
    session_key = models.CharField(max_length=300, null=True)
    state = models.IntegerField(null=True)
    user = models.OneToOneField(User, related_name='lastfm_connection')


class SpotifyConnection(models.Model):
    username = models.CharField(max_length=300, null=True)
    token = models.CharField(max_length=300, null=True)
    state = models.IntegerField(null=True)
    user = models.OneToOneField(User, related_name='spotify_connection')


class LastfmQuery(models.Model):
    task_id = models.CharField(max_length=300)
    track_results = models.ManyToManyField(LastfmTrack, null=True, through='LastfmQueryResult')


class LastfmQueryResult(models.Model):
    query = models.ForeignKey(LastfmQuery, on_delete=models.CASCADE)
    track = models.ForeignKey(LastfmTrack, on_delete=models.CASCADE)


class LastfmSearch(models.Model):
    track_name = models.CharField(max_length=300, null=True)
    artist_name = models.CharField(max_length=300, null=True)
    query = models.OneToOneField(LastfmQuery, related_name='search', null=True)
