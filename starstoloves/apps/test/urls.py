from django.conf.urls import patterns, include, url
from .views import results

urlpatterns = patterns('',
    url(r'^$', results, name='results'),
)
