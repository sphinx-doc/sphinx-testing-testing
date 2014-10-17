Changelog
==========

0.6.0 (2014-10-17)
-------------------
- Add python 3.2 support (with Sphinx < 1.3)
- Replace ListOutput with StringIO

0.5.2 (2014-10-16)
-------------------
- Fix bug:

   - Fix srcdir and confdir are not abspath

0.5.1 (2014-10-15)
-------------------
- Reimplement with_app decorator as class
- Set copy_srcdir_to_tmpdir=True if write_docstring is specified

0.5.0 (2014-10-15)
-------------------
- Add write_docstring option to with_app()

0.4.0 (2014-09-30)
-------------------
- Add pathlib like accessors to path class: parent, name, suffix and stem
- Fix bug:

   - #1 Fix exc assignment in with_app decorator.

0.3.0 (2014-09-27)
-------------------
- Rename sphinx.testing package to sphinx_testing

0.2.0 (2014-09-24)
-------------------
- Add path#utime() and path#listdir()
- Change interface of @with_app: Give `status` and `warning` to decorated function as a argument

0.1.0 (2014-09-20)
-------------------
- Initial release
