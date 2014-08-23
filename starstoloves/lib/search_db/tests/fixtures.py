from unittest.mock import patch

import pytest


def create_patch(request, module):
    patcher = patch(module)
    def fin():
        patcher.stop()
    request.addfinalizer(fin)
    return patcher.start()