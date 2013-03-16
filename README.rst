.. readme_:

django-template-debug
=====================

A small collection of template tags for debugging and introspecting Django templates

Documentation
*************
The documentation is hosted on Read the Docs and is available `here <http://readthedocs.org/docs/django-template-debug/en/latest/index.html>`_

Requirements
************
None, but the latest ipdb is highly recommended.

Installation
************

django-template-debug is available on pypi, so the easiest way to install it 
is using pip::

    pip install django-template-debug

Setup
*****
Add 'template_debug' to the INSTALLED_APPS iterable in your settings file. For example::

    INSTALLED_APPS = (
        ...
        'template_debug',
        ...
    )

Add ``TEMPLATE_DEBUG = True`` to your local or development settings if it is not already set.

- Unless TEMPLATE_DEBUG is set to True, the django-template-debug templates will return an empty string without doing anything. This behavior prevents your application from calling set_trace() or print in a production environment if django-template-debug template tags are accidentally commited and deployed.
