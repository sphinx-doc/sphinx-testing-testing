# -*- coding: utf-8 -*-

import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

if sys.version_info < (3,):
    unittest.TestCase.assertCountEqual = unittest.TestCase.assertItemsEqual

if sys.version_info < (3, 3):
    from mock import patch
else:
    from unittest.mock import patch

import os
import sphinx
from six import StringIO
from sphinx_testing.path import path
from sphinx_testing.tmpdir import mkdtemp
from sphinx_testing.util import TestApp, with_app


class TestSphinxTesting(unittest.TestCase):
    def test_TestApp(self):
        try:
            srcdir = path(__file__).dirname() / 'examples'
            app = TestApp(srcdir=srcdir)
            self.assertIsInstance(app._status, StringIO)
            self.assertIsInstance(app._warning, StringIO)

            if sphinx.__version__ < '1.0.0':
                app.build(True, None)
            else:
                app.build()
            self.assertIn('index.html', os.listdir(app.outdir))
        finally:
            app.cleanup()

    def test_TestApp_when_srcdir_specified(self):
        try:
            srcdir = path(__file__).dirname() / 'examples'
            app = TestApp(srcdir=srcdir)
            self.assertEqual(srcdir, app.srcdir)
            self.assertNotEqual(app.srcdir, app.builddir.dirname())
            self.assertTrue(app.builddir.isdir())
            self.assertCountEqual(['conf.py', 'index.rst'],
                                  os.listdir(app.srcdir))
            self.assertEqual((srcdir / 'conf.py').read_text(),
                             (app.srcdir / 'conf.py').read_text())
            self.assertEqual((srcdir / 'index.rst').read_text(),
                             (app.srcdir / 'index.rst').read_text())
        finally:
            app.cleanup()

        self.assertFalse(app.builddir.exists())

    def test_TestApp_when_srcdir_is_None(self):
        with self.assertRaises(AssertionError):
            TestApp(srcdir=None)

    def test_TestApp_when_create_new_srcdir(self):
        try:
            app = TestApp(create_new_srcdir=True)
            self.assertIsNotNone(app.srcdir)
            self.assertEqual(['conf.py'], os.listdir(app.srcdir))
            self.assertEqual('', (app.srcdir / 'conf.py').read_text())
        finally:
            app.cleanup()

    def test_TestApp_when_srcdir_and_create_new_srcdir_conflict(self):
        with self.assertRaises(AssertionError):
            TestApp(srcdir='examples', create_new_srcdir=True)

    def test_TestApp_when_copy_srcdir_to_tmpdir(self):
        try:
            srcdir = path(__file__).dirname() / 'examples'
            app = TestApp(srcdir=srcdir, copy_srcdir_to_tmpdir=True)
            self.assertNotEqual(srcdir, app.srcdir)
            self.assertEqual(app.srcdir, app.builddir.dirname())
            self.assertTrue(app.builddir.isdir())
            self.assertCountEqual(['_build', 'conf.py', 'index.rst'],
                                  os.listdir(app.srcdir))
            self.assertEqual((srcdir / 'conf.py').read_text(),
                             (app.srcdir / 'conf.py').read_text())
            self.assertEqual((srcdir / 'index.rst').read_text(),
                             (app.srcdir / 'index.rst').read_text())
        finally:
            app.cleanup()

        self.assertFalse(app.srcdir.exists())
        self.assertFalse(app.builddir.exists())

    def test_TestApp_cleanup(self):
        app = TestApp(create_new_srcdir=True)
        self.assertTrue(app.builddir.exists())

        with patch("sphinx.theming.Theme") as Theme:
            with patch("sphinx.ext.autodoc.AutoDirective") as AutoDirective:
                app.cleanup()
                self.assertEqual(1, Theme.themes.clear.call_count)
                self.assertEqual(1, AutoDirective._registry.clear.call_count)
                self.assertFalse(app.builddir.exists())

    def test_TestApp_cleanup_when_cleanup_on_errors(self):
        app = TestApp(create_new_srcdir=True, cleanup_on_errors=False)
        self.assertTrue(app.builddir.exists())

        with patch("sphinx.theming.Theme") as Theme:
            with patch("sphinx.ext.autodoc.AutoDirective") as AutoDirective:
                app.cleanup(error=True)
                self.assertEqual(0, Theme.themes.clear.call_count)
                self.assertEqual(0, AutoDirective._registry.clear.call_count)
                self.assertTrue(app.builddir.exists())

        with patch("sphinx.theming.Theme") as Theme:
            with patch("sphinx.ext.autodoc.AutoDirective") as AutoDirective:
                app.cleanup(error=None)
                self.assertEqual(1, Theme.themes.clear.call_count)
                self.assertEqual(1, AutoDirective._registry.clear.call_count)
                self.assertFalse(app.builddir.exists())

    def test_with_app(self):
        srcdir = path(__file__).dirname() / 'examples'
        builddir = []

        @with_app(srcdir=srcdir, copy_srcdir_to_tmpdir=True)
        def execute(app, status, warning):
            (app.srcdir / 'unknown.rst').write_text('')
            builddir.append(app.builddir)  # store to check outside of func
            if sphinx.__version__ < '1.0.0':
                app.build(True, None)
            else:
                app.build()

            self.assertIsInstance(status, StringIO)
            self.assertIsInstance(warning, StringIO)
            self.assertIn('index.html', os.listdir(app.outdir))
            self.assertIn('Running Sphinx', status.getvalue())
            self.assertIn("WARNING: document isn't included in any toctree",
                          warning.getvalue())

        execute()
        self.assertFalse(builddir[0].exists())

    @patch("sphinx_testing.util.mkdtemp")
    def test_with_app_bad_args(self, _mkdtemp):
        tmpdir = _mkdtemp.return_value = mkdtemp()
        srcdir = path(__file__).dirname() / 'examples'

        @with_app(srcdir=srcdir, copy_srcdir_to_tmpdir=True)
        def execute(oops):
            pass

        with self.assertRaises(TypeError):
            # TypeError: execute() takes 1 positional argument but 3 were given
            execute()

        self.assertFalse(tmpdir.exists())

    def test_with_app_write_docstring1(self):
        srcdir = path(__file__).dirname() / 'examples'

        @with_app(srcdir=srcdir, copy_srcdir_to_tmpdir=True,
                  write_docstring=True)
        def execute(app, status, warning):
            """ Hello world """
            content = (app.srcdir / 'index.rst').read_text()
            self.assertEqual('Hello world ', content)

        execute()

    def test_with_app_write_docstring2(self):
        srcdir = path(__file__).dirname() / 'examples'

        @with_app(srcdir=srcdir, copy_srcdir_to_tmpdir=True,
                  write_docstring='hello.rst')
        def execute(app, status, warning):
            """ Hello world """
            content = (app.srcdir / 'hello.rst').read_text()
            self.assertEqual('Hello world ', content)

        execute()
