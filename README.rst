|doc-master| |pypi-lastrelease| |python-versions|
|project-status| |project-license| |project-format|
|project-implementation|

.. |doc-master| image:: https://readthedocs.org/projects/dirty-models-sphinx/badge/?version=latest
    :target: http://dirty-models-sphinx.readthedocs.io/?badge=latest
    :alt: Documentation Status

.. |pypi-lastrelease| image:: https://img.shields.io/pypi/v/dirty-models-sphinx.svg
    :target: https://pypi.python.org/pypi/dirty-models-sphinx/
    :alt: Latest Version

.. |python-versions| image:: https://img.shields.io/pypi/pyversions/dirty-models-sphinx.svg
    :target: https://pypi.python.org/pypi/dirty-models-sphinx/
    :alt: Supported Python versions

.. |project-status| image:: https://img.shields.io/pypi/status/dirty-models-sphinx.svg
    :target: https://pypi.python.org/pypi/dirty-models-sphinx/
    :alt: Development Status

.. |project-license| image:: https://img.shields.io/pypi/l/dirty-models-sphinx.svg
    :target: https://pypi.python.org/pypi/dirty-models-sphinx/
    :alt: License

.. |project-format| image:: https://img.shields.io/pypi/format/dirty-models-sphinx.svg
    :target: https://pypi.python.org/pypi/dirty-models-sphinx/
    :alt: Download format

.. |project-implementation| image:: https://img.shields.io/pypi/implementation/dirty-models-sphinx.svg
    :target: https://pypi.python.org/pypi/dirty-models-sphinx/
    :alt: Supported Python implementations

.. _Dirty Models: http://dirty-models.readthedocs.io/

.. _Dirty Validators: https://github.com/alfred82santa/dirty-validators

.. _Sphinx: http://www.sphinx-doc.org

.. _autodoc: http://www.sphinx-doc.org/en/stable/ext/autodoc.html?highlight=autodoc#module-sphinx.ext.autodoc

=============================
Dirty Models Sphinx extension
=============================

`Sphinx`_ extension for dirty models


-----
About
-----

`Sphinx`_ extension to help developers to write documentation of
applications which use `Dirty Models`_.


Features
========

* Describe each field with real type.

* All field types defined on `Dirty Models`_ are documented.

* Use prefixed (doc comment using ``#:`` before field) or
  suffixed (Multiline doc string after field) documentation for each field.

* Document ``read only`` fields.

* Document default value for each field.

* Document datetime format on those fields.


------------
Installation
------------

Just use ``pip`` to install it:

.. code-block:: bash

    $ pip install dirty-models-sphinx

And add to `Sphinx`_ extensions on your project.

.. warning::

    `autodoc`_ extension (included in Sphinx) is required.

**conf.py file:**

.. code-block:: python

    extensions = [
        'sphinx.ext.autodoc',
        'dirty_models_sphinx'
    ]

-----
Usage
-----

Just use regular autodocumenter:

.. code-block:: rst

    .. automodule:: models
        :members:
        :show-inheritance:


------
Future
------

* Document `Dirty Validators`_.

* Document basic validations.

-------------
Documentation
-------------

http://dirty-models-sphinx-extension.readthedocs.io