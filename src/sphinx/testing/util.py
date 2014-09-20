# -*- coding: utf-8 -*-
"""
    Sphinx test suite utilities
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2007-2014 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import shutil
from six import StringIO
from functools import wraps

from sphinx.application import Sphinx
from sphinx.testing.path import path
from sphinx.testing.tmpdir import mkdtemp


class ListOutput(object):
    """
    File-like object that collects written text in a list.
    """
    def __init__(self, name):
        self.name = name
        self.content = []

    def reset(self):
        del self.content[:]

    def write(self, text):
        self.content.append(text)


class TestApp(Sphinx):
    """
    A subclass of :class:`Sphinx` that runs on the test root, with some
    better default values for the initialization parameters.
    """

    def __init__(self, srcdir=None, confdir=None, outdir=None, doctreedir=None,
                 buildername='html', confoverrides=None, status=None,
                 warning=None, freshenv=False, warningiserror=False, tags=None,
                 cleanenv=False, copy_srcdir_to_tmpdir=False,
                 create_new_srcdir=False, cleanup_on_errors=True):
        self.cleanup_trees = []
        self.cleanup_on_errors = cleanup_on_errors

        if create_new_srcdir:
            assert srcdir is None, 'conflicted: create_new_srcdir, srcdir'
            tmpdir = mkdtemp()
            self.cleanup_trees.append(tmpdir)
            tmproot = tmpdir / 'root'
            tmproot.makedirs()
            (tmproot / 'conf.py').write_text('')
            srcdir = tmproot

        assert srcdir is not None, 'srcdir not found'
        srcdir = path(srcdir)

        if copy_srcdir_to_tmpdir:
            tmpdir = mkdtemp()
            self.cleanup_trees.append(tmpdir)
            tmproot = tmpdir / srcdir.basename()
            srcdir.copytree(tmproot)
            srcdir = tmproot

        self.builddir = srcdir.joinpath('_build')
        if confdir is None:
            confdir = srcdir
        if outdir is None:
            outdir = srcdir.joinpath(self.builddir, buildername)
            if not outdir.isdir():
                outdir.makedirs()
            self.cleanup_trees.insert(0, outdir)
        if doctreedir is None:
            doctreedir = srcdir.joinpath(srcdir, self.builddir, 'doctrees')
            if not doctreedir.isdir():
                doctreedir.makedirs()
            if cleanenv:
                self.cleanup_trees.insert(0, doctreedir)
        if confoverrides is None:
            confoverrides = {}
        if status is None:
            status = StringIO()
        if warning is None:
            warning = ListOutput('stderr')

        Sphinx.__init__(self, srcdir, confdir, outdir, doctreedir,
                        buildername, confoverrides, status,
                        warning, freshenv, warningiserror, tags)

    def __repr__(self):
        classname = self.__class__.__name__
        return '<%s buildername=%r>' % (classname, self.builder.name)

    def cleanup(self, error=None):
        from sphinx.theming import Theme
        from sphinx.ext.autodoc import AutoDirective

        if error and self.cleanup_on_errors is False:
            return

        Theme.themes.clear()
        AutoDirective._registry.clear()
        for tree in self.cleanup_trees:
            shutil.rmtree(tree, True)


def with_app(*sphinxargs, **sphinxkwargs):
    """
    Make a TestApp with args and kwargs, pass it to the test and clean up
    properly.
    """
    def testcase(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            app = None
            exc = None
            try:
                app = TestApp(*sphinxargs, **sphinxkwargs)
                func(*(args + (app,)), **kwargs)
            except Exception as exc:
                raise  # store exception to `exc` variable
            finally:
                if app:
                    if exc:
                        app.cleanup(error=exc)
                    else:
                        app.cleanup()
        return decorator
    return testcase
