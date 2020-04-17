|doc-master| |pypi-lastrelease| |python-versions|
|project-status| |project-license| |project-format|
|project-implementation|

.. |doc-master| image:: https://readthedocs.org/projects/dirty-models-sphinx-extension/badge/?version=latest
    :target: http://dirty-models-sphinx-extension.readthedocs.io/?badge=latest
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

.. _Dirty Models Sphinx extension: http://dirty-models-sphinx-extension.readthedocs.io

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

* Able to set a prefix text in model signature.

* Able to set a prefix text in fields signature.

* Able to document field type as annotation or as field directive.

* Able to add models to ``toctree``.

* Able to add model attributes to ``toctree``.

* Able to describe model as structure.


Changelog
=========

Version 0.6.1
-------------

* Remove deprecated dependencies in `Sphinx`_ 3.0.0.
* Added documentation for `HashMapModels` with hardcoded field type.
* Fixes.


Version 0.6.0
-------------

* Use `access_mode` of `Dirty Models`_ version `0.12.0`.


Version 0.5.1
-------------

* Fix regressions.


Version 0.5.0
-------------

* Added option to describe model as structure.
* Added enum documenter.
* Added option to hide/show alias.
* Added option to hide/show read-only tag.
* Added option to use custom title as model name.
* No document fields with key `hidden` set to true on field metadata.
* Better field type handling.
* New module autodocumenter `autodirtymodule` in order to allow to set new options at module level.


Version 0.4.1
-------------

* Fix installation.


Version 0.4.0
-------------

* Document default timezone on TimeField and DatetimeField.
* Document forced timezone on DatetimeField.
* Minor fixes.
* Fix nested classes.
* Document EnumField.


Version 0.3.0
-------------

* Added option to add models to ``toctree``.
* Added option to add model attributes to ``toctree``.
* Added option to set prefix model signature.
* Added option to set prefix model field signature.
* Added option to use field type as annotation.
* Added fields to index.
* Changed default value label to ``Default value``.


Issues
======

* Latex manual document class builder fails when model attributes are in ``toctree``.
  That is because it creates a fake sections with same ``ids`` and remove after ``toctree`` is created.
  So, latex builder does not found references when it try to create links.


------------
Installation
------------

Just use ``pip`` to install it:

.. code-block:: bash

    $ pip install dirty-models-sphinx

And add to `Sphinx`_ extensions to your project.

.. warning::

    `autodoc`_ extension (included in Sphinx) is required.

**conf.py file:**

.. code-block:: python

    extensions = [
        'sphinx.ext.autodoc',
        'dirty_models_sphinx'
    ]


-------------
Configuration
-------------

It is possible to modify `Dirty Models Sphinx extension`_ behavior using configuration in ``conf.py`` file.

**dirty_model_add_classes_to_toc**

    If it is ``True`` Dirty Models classes will be added to table of content. Default: ``True``.

**dirty_model_add_attributes_to_toc**

    If it is ``True`` Dirty Models class attributes will be added to table of content, only if classes were added.
    Default: ``True``.

**dirty_model_class_label**

    It defines a prefix text for Dirty Model class signatures. It is possible to use ``None`` in order to avoid prefix.
    Default: ``'Model'``.

**dirty_model_property_label**

    It defines a prefix text for Dirty Model class field signatures. It is possible to use ``None`` in
    order to avoid prefix. Default: ``'property'``.

**dirty_enum_label**

    It defines a prefix text for enumearions signatures. It is possible to use ``None`` in
    order to avoid prefix. Default: ``'Enum'``.

**dirty_model_hide_alias**

    It allows to hide field alias.

**dirty_model_hide_readonly**

    It allows to hide read-only tags.

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