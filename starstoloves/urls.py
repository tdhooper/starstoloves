from django.conf.urls import patterns, include, url
import views

urlpatterns = patterns('',
    url(r'^$',                      views.index),
    url(r'^connect-lastfm/$',       views.connectLastfm),
    url(r'^disconnect-lastfm/$',    views.disconnectLastfm),
    url(r'^disconnect-spotify/$',   views.disconnectSpotify),
)