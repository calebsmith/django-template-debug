django-template-debug
=====================

A small collection of template tags for debugging and introspecting templates


Installation
************

Packaging on pypi isn't complete yet. For now you'll need to clone the repo
into your virtualenv's site-packages, or pip install the egg from github directly.


Setup
*****
Go to your local settings.py (be sure the settings file is not used for a production environment)
and add 'template_debug' to your installed apps via::

    INSTALLED_APPS.append('template_debug')

N.B. - You will need to change your INSTALLED_APPS setting to a list in your base settings.py if it is a tuple.

Add the following to your local_settings.py::

    TEMPLATE_DEBUG = True

Without this setting, the debug templates will return without doing anything.
This behavior prevents your application from calling set_trace() or print in a production environment
if some stray tags are committed in your templates.


Examples
********

To use django-template-debug simply load the debug tags in a template as follows::

    {% load debug_tags %}

Be sure to put your tags inside of a section that you are certain will be rendered.
(e.g. make sure the tags are not inside of if tags or not inside of a block tag when needed)

The available tags are outlined below:

{% set_trace %}
    - Starts a set_trace while the template is being rendered. The context is 
      available inside of this tag as the variable 'context'. ipdb is used if 
      available; otherwise the tag falls back to pdb.

{% attributes <variable_name> %}
    - Prints the attributes of the variable provided to the console using dir()

{% details <variable_name> %}
    - Prints a dictionary in the pattern {attribute: value} of the variable 
      provided to the console for any attribute's value that can be obtained 
      without raising an exception.
