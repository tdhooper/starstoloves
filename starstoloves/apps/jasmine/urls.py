from django.conf.urls import patterns, include, url
from .views import spec_runner

urlpatterns = patterns('',
    url(r'^$', spec_runner, name='spec_runner'),
)
