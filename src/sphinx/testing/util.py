# -*- coding: utf-8 -*-
"""
    Sphinx test suite utilities
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2007-2014 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import shutil
import tempfile
from six import StringIO
from functools import wraps

from sphinx import application
from sphinx.theming import Theme
from sphinx.ext.autodoc import AutoDirective
from sphinx.testing.path import path


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


class TestApp(application.Sphinx):
    """
    A subclass of :class:`Sphinx` that runs on the test root, with some
    better default values for the initialization parameters.
    """

    def __init__(self, srcdir=None, confdir=None, outdir=None, doctreedir=None,
                 buildername='html', confoverrides=None,
                 status=None, warning=None, freshenv=None,
                 warningiserror=None, tags=None,
                 confname='conf.py', cleanenv=False,
                 _copy_to_temp=False,
                 ):

        application.CONFIG_FILENAME = confname

        self.cleanup_trees = []

        if srcdir == '(empty)':
            tempdir = path(tempfile.mkdtemp())
            self.cleanup_trees.append(tempdir)
            temproot = tempdir / 'root'
            temproot.makedirs()
            (temproot / 'conf.py').write_text('')
            srcdir = temproot
        else:
            srcdir = path(srcdir)

        if _copy_to_temp:
            tempdir = path(tempfile.mkdtemp())
            self.cleanup_trees.append(tempdir)
            temproot = tempdir / srcdir.basename()
            srcdir.copytree(temproot)
            srcdir = temproot

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
        if freshenv is None:
            freshenv = False
        if warningiserror is None:
            warningiserror = False

        application.Sphinx.__init__(self, srcdir, confdir, outdir, doctreedir,
                                    buildername, confoverrides, status, warning,
                                    freshenv, warningiserror, tags)

    def cleanup(self, doctrees=False):
        Theme.themes.clear()
        AutoDirective._registry.clear()
        for tree in self.cleanup_trees:
            shutil.rmtree(tree, True)

    def __repr__(self):
        return '<%s buildername=%r>' % (self.__class__.__name__, self.builder.name)


def with_app(*args, **kwargs):
    """
    Make a TestApp with args and kwargs, pass it to the test and clean up
    properly.
    """
    def generator(func):
        @wraps(func)
        def deco(*args2, **kwargs2):
            app = TestApp(*args, **kwargs)
            func(app, *args2, **kwargs2)
            # don't execute cleanup if test failed
            app.cleanup()
        return deco
    return generator
