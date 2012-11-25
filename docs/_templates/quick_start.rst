.. _quick_start:

=================
Quick Start Guide
=================

Example Usage
*************

After installing django-template-debug, simply load the debug tags in a template as follows::

    {% load debug_tags %}

Be sure to put your debug tags inside of a section that you are certain will be rendered.
(e.g. make sure the tags are inside of a block tag that will be rendered and not inside of if tags)
Alternatively, you might insert a {% set_trace %} inside of a conditional or for loop to
determine if that branch is being executed in your template.

The available tags are outlined briefly below and described more extensively in their linked documentation:

- :ref:`set_trace` {% set_trace %}:
    - Drops the Django runserver into a set_trace debugger during template rendering
- :ref:`attributes` {% attributes <variable_name> %}:
    - Given a variable name, prints and returns its attributes that are accessible within a Django template
- :ref:`variables` {% variables %}:
    - Prints and returns the list of variables available inside of the current context
- :ref:`details` {% details <variable_name> %}:
    - Given a variable name, prints and returns a dictionary of the form {'attribute': value} for the attributes that are accessible within a Django template.
