django-template-debug
=====================

A small collection of template tags for debugging and introspecting templates


Installation
************

django-template-debug is available on pypi, so the easiest way to install it 
is using pip::

    pip install django-template-debug

Setup
*****
Go to your local settings.py (be sure the settings file is not used for a production environment)
and add 'template_debug' to your installed apps via::

    INSTALLED_APPS.append('template_debug')

N.B. - You will need to change your INSTALLED_APPS setting to a list in your base settings.py if it is a tuple
or do something like: INSTALLED_APPS = list(INSTALLED_APPS) + 'template_debug'

Add the following to your local_settings.py::

    TEMPLATE_DEBUG = True

Without this setting, the debug templates will return without doing anything.
This behavior prevents your application from calling set_trace() or print in a production environment
if django-template-debug is accidentally installed outside of the local settings.


Examples
********

To use django-template-debug simply load the debug tags in a template as follows::

    {% load debug_tags %}

Be sure to put your tags inside of a section that you are certain will be rendered.
(e.g. make sure the tags are not inside of if tags or not inside of a block tag when needed)
Alternatively, you might insert a {% set_trace %} inside of a conditional or for loop to
determine if that branch is being excetued in your template.

The available tags are outlined below:

{% set_trace %}
    - Starts a set_trace while the template is being rendered. The context is 
      available inside of this tag as the variable 'context'. ipdb is used if 
      available; otherwise the tag falls back to pdb.
    - Type 'availables' to see a list of variables inside of the context.
    - You can use context['variable_name'] or context.variable_name for
      convenience.

{% variables %}
    - Prints the variables available in the current context

{% details <variable_name> %}
    - Prints a dictionary in the pattern {attribute: value} of the variable 
      provided, for any attribute's value that can be obtained without raising 
      an exception or making a method call.

After entering the debugger, one can use details and variables as functions as follows::

    details(context.variable_name)
    variables(context)
