==============
sphinx-testing
==============

``sphinx-testing`` provides testing utility classes and functions for Sphinx extensions.

.. image:: https://travis-ci.org/sphinx-doc/sphinx-testing.svg?branch=master
   :target: https://travis-ci.org/sphinx-doc/sphinx-testing

.. image:: https://coveralls.io/repos/sphinx-doc/sphinx-testing/badge.png?branch=master
   :target: https://coveralls.io/r/sphinx-doc/sphinx-testing?branch=master

.. image:: https://pypip.in/d/sphinx-testing/badge.png
   :target: https://pypi.python.org/pypi/sphinx-testing/
   :alt: Number of PyPI downloads

.. image:: https://pypip.in/wheel/sphinx-testing/badge.png
   :target: https://pypi.python.org/pypi/sphinx-testing/
   :alt: Wheel Status

Setup
=====

Use easy_install or pip::

   $ sudo pip install sphinx-testing

Usage
======

Example::

    from sphinx_testing import with_app

    @with_app(buildername='html', srcdir='/path/to/examples', copy_srcdir_to_tmpdir=True)
    def test_sphinx_build(app, status, warning):
        app.build()
        html = (app.outdir / 'index.html').read_text()
        assert '<h1>Hello world</h1>' in html


Requirements
============
* Python 2.6, 2.7, 3.2 or later
* Sphinx 0.6 or later
* six

License
=======
BSD License
