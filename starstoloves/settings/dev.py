from .base import *

DEBUG = True

INSTALLED_APPS = INSTALLED_APPS + (
    'starstoloves.apps.jasmine',
    'starstoloves.apps.test',
    'starstoloves.apps.style',
)

try:
    from .local import *
except ImportError:
    pass
