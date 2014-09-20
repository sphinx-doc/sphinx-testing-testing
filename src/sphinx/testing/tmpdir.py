# -*- coding: utf-8 -*-
"""
    tmpdir utilities
    ~~~~~~~~~~~~~~~~

    :copyright: Copyright 2007-2014 by the Sphinx team, see Sphinx-AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import tempfile
from functools import wraps
from sphinx.testing.path import path


def with_tempdir(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        try:
            tmpdir = path(tempfile.mkdtemp())
            args = args + (tmpdir,)  # extends argument; add tmpdir at tail
            return func(*args, **kwargs)
        finally:
            tmpdir.rmtree()
    return decorator
