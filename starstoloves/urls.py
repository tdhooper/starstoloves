from django.conf.urls import patterns, include, url
from starstoloves.views import main

urlpatterns = patterns('',
    url(r'^$',                      main.index, name='index'),
    url(r'^connect-lastfm/$',       main.connectLastfm, name='connect_lastfm'),
    url(r'^disconnect-lastfm/$',    main.disconnectLastfm, name='disconnect_lastfm'),
    url(r'^disconnect-spotify/$',   main.disconnectSpotify, name='disconnect_spotify'),
)