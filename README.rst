.. readme_:

django-template-debug
=====================

A small collection of template tags for debugging and introspecting Django templates

`Documentation <http://readthedocs.org/docs/django-template-debug/en/latest/index.html>`_

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

Usage
*****

Add {% load debug_tags %} in any Django template.

The available tags to use are {% set_trace %} {% variables %} {% attributes varname %} and {% details varname %}

See `Example Usage <https://django-template-debug.readthedocs.org/en/latest/_templates/quick_start.html#example-usage>`_ docs for more details

Developer Setup
***************

Create a fresh virtualenv and install the test requirements::

    mkvirtualenv template-debug
    pip install -r requirements/test.txt

Use manage.py in the project directory along with the example.settings file
for local testing.

To run unittests using the virtualenv's Python and Django, use the `runtests`
script. To test all supported versions of Python and Django, run the unittests
using tox.
