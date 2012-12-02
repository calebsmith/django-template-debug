.. _variables:

=========
Variables
=========

Syntax: {% variables %}

Prints and returns the variables available in the current context. This will include the context provided by the view that called the current template as well as any context processors that are in use.

Example: {% variables %} -> ['user', 'csrf_token', 'items']
