django-template-debug
=====================

A small collection of template tags for debugging and introspecting templates

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
In your local settings.py (be sure the settings file is not used for a production environment)
add 'template_debug' to your installed apps via::

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
(e.g. make sure the tags are inside of a block tag that will be rendered and not inside of if tags)
Alternatively, you might insert a {% set_trace %} inside of a conditional or for loop to
determine if that branch is being executed in your template.

The available tags are outlined below:

{% set_trace %}
    - Starts a set_trace while the template is being rendered. ipdb is used if 
      available; otherwise the tag falls back to pdb.
    - The context is available inside of the set_trace as `context`.
    - Type 'availables' to see a list of variables inside of the context.
    - Most importantly, the variables available inside of the context are available in the local scope as <variable_name>
      (e.g. If a variables 'items' is in the context, it is available in the set trace as the variable 'items')

{% variables %}
    - Prints the variables available in the current context

{% details <variable_name> %}
    - Prints a dictionary in the pattern {attribute: value} of the variable 
      provided, for any attribute's value that can be obtained without raising 
      an exception or making a method call.

When using {% set_trace %}, one can use details and variables as functions as follows::

    details(variable_name)
    variables(context)

Type 'c' to continue rendering the template as normal
