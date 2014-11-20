Profile Management Admin Interface
==================================

POEM Admin interface is based on Django admin with a few added extensions. There are no additional views implemented and thus the interface is fully auto-generated. This documentation has the following parts:
 * Model (:py:mod:`poem.models`), also see `POEM model <https://tomtools.cern.ch/confluence/display/SAM/Model>`_ 
 * Admin extensions (:py:mod:`poem.admin`, :py:mod:`poem.admin_ext`)
 * Context processors (:py:mod:`poem.context_processors`)
 * Widgets (:py:mod:`poem.widgets`)
 * django-taggit extension (:py:mod:`poem.taggit_ext`)
 * Management commands (:doc:`poem.management.commands`)

:mod:`models` Module
--------------------

.. automodule:: poem.models
    :members:
    :show-inheritance:

:mod:`admin` Module
-------------------

.. automodule:: poem.admin
    :members:
    :show-inheritance:

:mod:`admin_ext` Module
-----------------------

.. automodule:: poem.admin_ext
    :members:
    :show-inheritance:

:mod:`context_processors` Module
--------------------------------

.. automodule:: poem.context_processors
    :members:
    :undoc-members:
    :show-inheritance:


:mod:`widgets` Module
---------------------

.. automodule:: poem.widgets
    :members:
    :undoc-members:
    :show-inheritance:

:mod:`taggit_ext` Module
------------------------

.. automodule:: poem.taggit_ext
    :members:
    :undoc-members:
    :show-inheritance:

Subpackages
-----------

.. toctree::

    poem.management.commands
    poem.templatetags

