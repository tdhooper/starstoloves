import os

APP_ROOT = os.path.join(os.path.dirname(__file__), '..')

try:
    from .local import *
except ImportError:
    pass
