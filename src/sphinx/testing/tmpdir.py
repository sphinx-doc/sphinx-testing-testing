# -*- coding: utf-8 -*-
"""
    tmpdir utilities
    ~~~~~~~~~~~~~~~~

    :copyright: Copyright 2007-2014 by the Sphinx team, see Sphinx-AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import tempfile
from sphinx.testing.path import path


def with_tempdir(func):
    def new_func(*args, **kwds):
        tempdir = path(tempfile.mkdtemp())
        func(tempdir, *args, **kwds)
        tempdir.rmtree()
    new_func.__name__ = func.__name__
    return new_func
