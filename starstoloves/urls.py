from django.conf.urls import patterns, include, url
from starstoloves.views import main, connection

urlpatterns = patterns('',
    url(r'^$',                      main.index, name='index'),
    url(r'^connect-lastfm/$',       connection.connect_lastfm, name='connect_lastfm'),
    url(r'^connect-spotify/$',      connection.connect_spotify, name='connect_spotify'),
    url(r'^disconnect-lastfm/$',    main.disconnect_lastfm, name='disconnect_lastfm'),
    url(r'^disconnect-spotify/$',   main.disconnect_spotify, name='disconnect_spotify'),
    url(r'^reload-lastfm/$',        main.reload_lastfm, name='reload_lastfm'),
    url(r'^reload-spotify/$',       main.reload_spotify, name='reload_spotify'),
    url(r'^result-update$',         main.result_update, name='result_update'),
    url(r'^love-tracks$',           main.love_tracks, name='love_tracks'),

    url(r'^specs/', include('starstoloves.apps.jasmine.urls', namespace='specs')),
    url(r'^test/', include('starstoloves.apps.test.urls', namespace='test')),
)