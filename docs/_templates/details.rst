.. _details:

=======
Details
=======

Syntax: {% details <variable_name> %}

Prints and returns a dictionary in the pattern {attribute: value} of the variable provided, for any attribute's value that can be obtained without raising an exception or making a method call.


The exact behavior is as follows:
    - Only attributes or methods that are accessible inside of Django templates are shown. This functionality is shared with the attributes tag. See :ref:`attributes` for further details.
    - Any routine (function or method) returns with the value 'routine' rather than being called. This prevents the execution of user defined routines with side-effects that alter data or make network requests.
    - ORM managers return with 'ManyRelatedManager' or 'RelatedManager' to improve readability of the output when an ORM instance is given as the input.

Example: {% details request.user %} -> { 'first_name': 'Joe', 'last_name': 'Sixpauk', 'set_password': 'routine', ...}
