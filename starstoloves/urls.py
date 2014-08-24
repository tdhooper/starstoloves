from django.conf.urls import patterns, include, url
from starstoloves.views import main

urlpatterns = patterns('',
    url(r'^$',                      main.index, name='index'),
    url(r'^connect-lastfm/$',       main.connect_lastfm, name='connect_lastfm'),
    url(r'^disconnect-lastfm/$',    main.disconnect_lastfm, name='disconnect_lastfm'),
    url(r'^disconnect-spotify/$',   main.disconnect_spotify, name='disconnect_spotify'),
    url(r'^result-update$',         main.result_update, name='result_update'),

    url(r'^specs/', include('starstoloves.apps.jasmine.urls', namespace='specs')),
    url(r'^test/', include('starstoloves.apps.test.urls', namespace='test')),
)