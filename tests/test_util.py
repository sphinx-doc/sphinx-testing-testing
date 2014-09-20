# -*- coding: utf-8 -*-

import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

if sys.version_info < (3, 3):
    from mock import patch
else:
    from unittest.mock import patch

import os
import shutil
import sphinx
from six import StringIO
from sphinx.testing.path import path
from sphinx.testing.util import ListOutput, TestApp, with_app


class TestSphinxTesting(unittest.TestCase):
    def test_ListOutput(self):
        output = ListOutput('name')
        self.assertEqual('name', output.name)
        self.assertEqual([], output.content)

        output.write('Hello')
        self.assertEqual(['Hello'], output.content)

        output.write('World')
        self.assertEqual(['Hello', 'World'], output.content)

        output.reset()
        self.assertEqual([], output.content)

    def test_TestApp(self):
        try:
            srcdir = path(__file__).dirname() / 'examples'
            app = TestApp(srcdir=srcdir)
            self.assertIsInstance(app._status, StringIO)
            self.assertIsInstance(app._warning, ListOutput)

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
            self.assertEqual(['conf.py', 'index.rst'],
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
            self.assertEqual(['_build', 'conf.py', 'index.rst'],
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

        @with_app(srcdir=srcdir)
        def execute(app):
            builddir.append(app.builddir)  # store to check outside of func
            if sphinx.__version__ < '1.0.0':
                app.build(True, None)
            else:
                app.build()

            self.assertIn('index.html', os.listdir(app.outdir))

        execute()
        self.assertFalse(builddir[0].exists())
