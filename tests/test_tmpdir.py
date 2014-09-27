# -*- coding: utf-8 -*-

import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import shutil
from sphinx_testing.path import path
from sphinx_testing.tmpdir import mkdtemp, with_tmpdir


class TestTmpdir(unittest.TestCase):
    def test_mkdtemp(self):
        try:
            tmpdir = mkdtemp()
            self.assertIsInstance(tmpdir, path)
        finally:
            shutil.rmtree(tmpdir)

        # prefix option
        try:
            tmpdir = mkdtemp(prefix='sphinx')
            self.assertTrue(tmpdir.basename().startswith('sphinx'))
        finally:
            tmpdir.rmtree()

        # suffix option
        try:
            tmpdir = mkdtemp(suffix='sphinx')
            self.assertTrue(tmpdir.basename().endswith('sphinx'))
        finally:
            tmpdir.rmtree()

        # dir option
        try:
            parent = mkdtemp()
            tmpdir = mkdtemp(dir=parent)
            self.assertTrue(parent, tmpdir.dirname())
        finally:
            parent.rmtree()

    def test_with_tmpdir(self):
        @with_tmpdir
        def testcase1(tmpdir):
            self.assertTrue(tmpdir.isdir())
            return tmpdir

        tmpdir = testcase1()
        self.assertFalse(tmpdir.isdir())

        @with_tmpdir
        def testcase2(tmpdir):
            self.assertTrue(tmpdir.isdir())
            raise Exception(tmpdir)

        try:
            testcase2()
        except Exception as exc:
            tmpdir = exc.args[0]
            self.assertFalse(tmpdir.isdir())
