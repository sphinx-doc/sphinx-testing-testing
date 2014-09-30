# -*- coding: utf-8 -*-

import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

if sys.version_info < (3,):
    unittest.TestCase.assertCountEqual = unittest.TestCase.assertItemsEqual

import os
import shutil
from tempfile import mkdtemp
from sphinx_testing import with_tmpdir
from sphinx_testing.path import path


class TestPath(unittest.TestCase):
    def test_instantiate(self):
        p = path('/path/to/file')
        self.assertIsInstance(p, path)
        self.assertEqual('/path/to/file', p)

    def test_suffix(self):
        p = path('/path/to/file.ext')
        self.assertEqual(".ext", p.suffix)
        self.assertEqual("/path/to/file", p.stem)

    def test_basename(self):
        p = path('/path/to/file')
        self.assertEqual("file", p.basename())
        self.assertEqual("file", p.name)

    def test_dirname(self):
        p = path('/path/to/file')
        self.assertIsInstance(p.dirname(), path)
        self.assertEqual("/path/to", p.dirname())
        self.assertEqual("/path/to", p.parent)
        self.assertEqual("/path", p.dirname().dirname())
        self.assertEqual("/", p.dirname().dirname().dirname())

    def test_abspath(self):
        p = path('.')
        self.assertIsInstance(p.abspath(), path)
        self.assertEqual(os.getcwd(), p.abspath())

    def test_isabs(self):
        p = path('path/to/file')
        self.assertFalse(p.isabs())

        p = path('/path/to/file')
        self.assertTrue(p.isabs())

    def test_isdir(self):
        p = path(__file__)
        self.assertFalse(p.isdir())  # file
        self.assertTrue(p.dirname().isdir())  # directory

        p = path('/path/to/file')  # not exists
        self.assertFalse(p.isdir())

    def test_isfile(self):
        p = path(__file__)
        self.assertTrue(p.isfile())  # file
        self.assertFalse(p.dirname().isfile())  # directory

        p = path('/path/to/file')  # not exists
        self.assertFalse(p.isfile())

    def test_islink(self):
        try:
            tmpdir = mkdtemp()
            symlink = "%s/test.symlink" % tmpdir
            os.symlink(__file__, symlink)

            p = path(symlink)
            self.assertTrue(p.islink())  # symlink

            p = path(__file__)
            self.assertFalse(p.islink())  # file
            self.assertFalse(p.dirname().islink())  # directory

            p = path('/path/to/file')  # not exists
            self.assertFalse(p.islink())
        finally:
            shutil.rmtree(tmpdir)

    def test_ismount(self):
        pass  # FIXME: to be test

    @with_tmpdir
    def test_rmtree(self, tmpdir):
        subdir = mkdtemp(dir=tmpdir)
        filename = "%s/entry.txt" % subdir
        open(filename, 'w').close()  # create empty file

        path(subdir).rmtree()
        self.assertFalse(os.path.exists(filename))
        self.assertFalse(os.path.exists(subdir))

        with self.assertRaises(OSError):
            path('/path/to/file').rmtree()

        path('/path/to/file').rmtree(ignore_errors=True)  # no exceptions

        # error handler
        result = []

        def onerror(func, path, exc_info):
            result.append((func, path, exc_info))

        path('/path/to/file').rmtree(onerror=onerror)
        self.assertNotEqual([], result)  # errors are stacked

    @with_tmpdir
    def test_copytree(self, tmpdir):
        subdir = mkdtemp(dir=tmpdir)
        subsubdir = "%s/subdir" % subdir
        filename = "%s/test.file" % subdir
        symlink = "%s/test.symlink" % subdir
        os.makedirs(subsubdir)
        open(filename, 'w').close()  # create empty file
        os.symlink(__file__, symlink)

        dstdir = os.path.join(tmpdir, "path/to/dstdir")
        path(subdir).copytree(dstdir)
        self.assertTrue(os.path.exists(subdir))
        self.assertTrue(os.path.exists(dstdir))
        self.assertTrue(os.path.isdir("%s/subdir" % dstdir))
        self.assertTrue(os.path.isfile("%s/test.file" % dstdir))
        self.assertTrue(os.path.isfile("%s/test.symlink" % dstdir))
        self.assertFalse(os.path.islink("%s/test.symlink" % dstdir))

        dstdir = os.path.join(tmpdir, "path/to/dstdir2")
        path(subdir).copytree(dstdir, symlinks=True)
        self.assertTrue(os.path.exists(subdir))
        self.assertTrue(os.path.exists(dstdir))
        self.assertTrue(os.path.isdir("%s/subdir" % dstdir))
        self.assertTrue(os.path.isfile("%s/test.file" % dstdir))
        self.assertTrue(os.path.isfile("%s/test.symlink" % dstdir))
        self.assertTrue(os.path.islink("%s/test.symlink" % dstdir))

    @with_tmpdir
    def test_move(self, tmpdir):
        subdir = mkdtemp(dir=tmpdir)
        subsubdir = "%s/subdir" % subdir
        filename = "%s/test.file" % subdir
        symlink = "%s/test.symlink" % subdir
        os.makedirs(subsubdir)
        open(filename, 'w').close()  # create empty file
        os.symlink(__file__, symlink)

        # rename
        dstdir = os.path.join(tmpdir, "dstdir")
        path(subdir).move(dstdir)
        self.assertFalse(os.path.exists(subdir))
        self.assertTrue(os.path.exists(dstdir))
        self.assertTrue(os.path.isdir("%s/subdir" % dstdir))
        self.assertTrue(os.path.isfile("%s/test.file" % dstdir))
        self.assertTrue(os.path.islink("%s/test.symlink" % dstdir))

        # move into the directory
        dstdir2 = mkdtemp(dir=tmpdir)
        dstsubdir = "%s/%s" % (dstdir2, os.path.basename(dstdir))
        path(dstdir).move(dstdir2)
        self.assertFalse(os.path.exists(dstdir))
        self.assertTrue(os.path.exists(dstdir2))
        self.assertTrue(os.path.exists(dstsubdir))

    @with_tmpdir
    def test_unlink(self, tmpdir):
        filename = "%s/test.file" % tmpdir
        symlink = "%s/test.symlink" % tmpdir
        open(filename, 'w').close()  # create empty file
        os.symlink(__file__, symlink)

        path(filename).unlink()
        self.assertFalse(os.path.exists(filename))

        path(symlink).unlink()
        self.assertFalse(os.path.exists(symlink))

    @with_tmpdir
    def test_utime(self, tmpdir):
        filename = "%s/test.file" % tmpdir
        open(filename, 'w').close()  # create empty file

        path(filename).utime((123, 456))
        self.assertEqual(123, os.stat(filename).st_atime)
        self.assertEqual(456, os.stat(filename).st_mtime)

    @with_tmpdir
    def test_listdir(self, tmpdir):
        subdir = "%s/subdir" % tmpdir
        filename = "%s/test.file" % tmpdir
        symlink = "%s/test.symlink" % tmpdir
        os.makedirs(subdir)
        open(filename, 'w').close()  # create empty file
        os.symlink(__file__, symlink)

        files = path(tmpdir).listdir()
        self.assertCountEqual(['subdir', 'test.file', 'test.symlink'], files)

    @with_tmpdir
    def test_write_text(self, tmpdir):
        filename = "%s/test.file" % tmpdir
        path(filename).write_text('hello world')

        text = open(filename).read()
        self.assertEqual('hello world', text)

    @with_tmpdir
    def test_read_text(self, tmpdir):
        filename = "%s/test.file" % tmpdir
        with open(filename, 'w') as fd:
            fd.write('hello world')

        self.assertEqual('hello world', path(filename).read_text())

    @with_tmpdir
    def test_write_bytes(self, tmpdir):
        filename = "%s/test.file" % tmpdir
        path(filename).write_bytes(b'hello world')

        text = open(filename, 'rb').read()
        self.assertEqual(b'hello world', text)

    @with_tmpdir
    def test_read_bytes(self, tmpdir):
        filename = "%s/test.file" % tmpdir
        with open(filename, 'wb') as fd:
            fd.write(b'hello world')

        self.assertEqual(b'hello world', path(filename).read_bytes())

    @with_tmpdir
    def test_exists(self, tmpdir):
        subdir = "%s/subdir" % tmpdir
        filename = "%s/test.file" % tmpdir
        symlink1 = "%s/test.symlink" % tmpdir
        symlink2 = "%s/test.symlink2" % tmpdir
        os.makedirs(subdir)
        open(filename, 'w').close()  # create empty file
        os.symlink(__file__, symlink1)
        os.symlink('/path/to/file', symlink2)

        # path#exists()
        self.assertTrue(path(subdir).exists())
        self.assertTrue(path(filename).exists())
        self.assertTrue(path(symlink1).exists())
        self.assertFalse(path(symlink2).exists())
        self.assertFalse(path('/path/to/file').exists())

        # path#lexists()
        self.assertTrue(path(subdir).lexists())
        self.assertTrue(path(filename).lexists())
        self.assertTrue(path(symlink1).lexists())
        self.assertTrue(path(symlink2).lexists())
        self.assertFalse(path('/path/to/file').lexists())

    @with_tmpdir
    def test_makedirs(self, tmpdir):
        try:
            umask = os.umask(0o000)  # reset umask at first

            subdir = "%s/path/to/subdir" % tmpdir
            path(subdir).makedirs()
            self.assertTrue(os.path.isdir(subdir))
            self.assertEqual(0o777, os.stat(subdir).st_mode & 0o777)

            subdir = "%s/another/path/to/subdir" % tmpdir
            path(subdir).makedirs(0o700)
            self.assertTrue(os.path.isdir(subdir))
            self.assertEqual(0o700, os.stat(subdir).st_mode & 0o777)
        finally:
            os.umask(umask)

    @with_tmpdir
    def test_jonpath(self, tmpdir):
        p = path('.')
        self.assertEqual('./path/to/file', p.joinpath('path/to/file'))
        self.assertEqual('/path/to/file', p.joinpath('/path/to/file'))

        self.assertEqual('./path/to/file', p / 'path/to/file')
        self.assertEqual('/path/to/file', p / '/path/to/file')
