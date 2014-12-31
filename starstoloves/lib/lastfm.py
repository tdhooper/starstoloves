from lastfm import lfm

from starstoloves import settings


lastfm_app = lfm.App(
    key=settings.LASTFM['key'],
    secret=settings.LASTFM['secret'],
    api_root='http://thirdparty.ws.past-loves-api.dev.audioscrobbler.com/2.0/',
)