.. _set_trace:

=========
Set Trace
=========

{% set_trace %}
    - Starts a set_trace while the template is being rendered. ipdb is used if 
      available; otherwise the pdb is used as a fallback.
    - The context is available inside of the set_trace as `context`.
    - Most importantly, the variables available inside of the context are available in the local scope as <variable_name>
      (e.g. If a variable 'items' is in the context, it is available in the set trace as the variable 'items')


When using {% set_trace %}, one can use details, attributes, and variables as functions as follows::

    details(variable_name)
    attributes(variable_name)
    variables(context)