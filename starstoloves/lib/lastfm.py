from lastfm import lfm

from starstoloves import settings


lastfm_app = lfm.App(settings.LASTFM['key'], settings.LASTFM['secret'])