from django.conf.urls import patterns, include, url
from views import main

urlpatterns = patterns('',
    url(r'^$',                      main.index),
    url(r'^connect-lastfm/$',       main.connectLastfm),
    url(r'^disconnect-lastfm/$',    main.disconnectLastfm),
    url(r'^disconnect-spotify/$',   main.disconnectSpotify),
)