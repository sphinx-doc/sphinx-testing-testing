# -*- coding: utf-8 -*-
"""
    Sphinx test suite utilities
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2007-2014 by the Sphinx team, see Sphinx-AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import shutil
from six import StringIO
from functools import wraps
from textwrap import dedent

from sphinx.application import Sphinx
from sphinx_testing.path import path
from sphinx_testing.tmpdir import mkdtemp


class TestApp(Sphinx):
    """
    A subclass of :class:`Sphinx` that runs on the test root, with some
    better default values for the initialization parameters.
    """

    def __init__(self, srcdir=None, confdir=None, outdir=None, doctreedir=None,
                 buildername='html', confoverrides=None, status=None,
                 warning=None, freshenv=False, warningiserror=False, tags=None,
                 copy_srcdir_to_tmpdir=False, create_new_srcdir=False,
                 cleanup_on_errors=True):
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
        srcdir = path(srcdir).abspath()

        if copy_srcdir_to_tmpdir:
            tmpdir = mkdtemp()
            self.cleanup_trees.append(tmpdir)
            tmproot = tmpdir / srcdir.basename()
            srcdir.copytree(tmproot)
            srcdir = tmproot
            self.builddir = srcdir.joinpath('_build')
        else:
            self.builddir = mkdtemp()
            self.cleanup_trees.append(self.builddir)

        if confdir is None:
            confdir = srcdir
        if outdir is None:
            outdir = self.builddir.joinpath(buildername)
            if not outdir.isdir():
                outdir.makedirs()
        if doctreedir is None:
            doctreedir = self.builddir.joinpath('doctrees')
            if not doctreedir.isdir():
                doctreedir.makedirs()
        if confoverrides is None:
            confoverrides = {}
        if status is None:
            status = StringIO()
        if warning is None:
            warning = StringIO()

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


class with_app(object):
    """
    Make a TestApp with args and kwargs, pass it to the test and clean up
    properly.
    """

    def __init__(self, *sphinxargs, **sphinxkwargs):
        self.sphinxargs = sphinxargs
        self.sphinxkwargs = sphinxkwargs

        self._write_docstring = sphinxkwargs.pop('write_docstring', False)
        if self._write_docstring:
            self.sphinxkwargs['copy_srcdir_to_tmpdir'] = True

    def write_docstring(self, basedir, docstring):
        if self._write_docstring:
            if self._write_docstring is True:
                filename = basedir / 'index.rst'
            else:
                filename = basedir / self._write_docstring

            filename.write_text(dedent(docstring), encoding='utf-8')

    def __call__(self, func):
        @wraps(func)
        def decorator(*args, **kwargs):
            app = None
            exc = None
            sphinxkwargs = dict(self.sphinxkwargs)  # create copy
            try:
                status = sphinxkwargs.setdefault('status', StringIO())
                warning = sphinxkwargs.setdefault('warning', StringIO())
                app = TestApp(*self.sphinxargs, **sphinxkwargs)
                self.write_docstring(app.srcdir, func.__doc__)

                func(*(args + (app, status, warning)), **kwargs)
            except Exception as _exc:
                exc = _exc
                raise
            finally:
                if app:
                    if exc:
                        app.cleanup(error=exc)
                    else:
                        app.cleanup()
        return decorator
