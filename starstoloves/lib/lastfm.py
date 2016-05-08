from lastfm import lfm

from starstoloves import settings


lastfm_app = lfm.App(
    key=settings.LASTFM['key'],
    secret=settings.LASTFM['secret'],
)