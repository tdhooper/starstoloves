from .base import *

DEBUG = True

try:
    from .local import *
except ImportError:
    pass