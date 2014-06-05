from .base import *

DEBUG = True

INSTALLED_APPS = INSTALLED_APPS + (
    'starstoloves.apps.jasmine',
)

try:
    from .local import *
except ImportError:
    pass
