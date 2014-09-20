# -*- coding: utf-8 -*-
"""
    tmpdir utilities
    ~~~~~~~~~~~~~~~~

    :copyright: Copyright 2007-2014 by the Sphinx team, see Sphinx-AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from functools import wraps
from sphinx.testing.path import path


def mkdtemp(suffix='', prefix='tmp', dir=None):
    import tempfile
    if isinstance(dir, path):
        tmpdir = tempfile.mkdtemp(suffix, prefix, str(dir))
    else:
        tmpdir = tempfile.mkdtemp(suffix, prefix, dir)

    return path(tmpdir)


def with_tmpdir(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        try:
            tmpdir = mkdtemp()
            args = args + (tmpdir,)  # extends argument; add tmpdir at tail
            return func(*args, **kwargs)
        finally:
            tmpdir.rmtree()
    return decorator
