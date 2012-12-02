.. _attributes:

==========
Attributes
==========

Syntax: {% attributes <variable_name> %}

Prints and returns the attributes of the variable that are available inside of Django templates.

This tag will not show methods that are inaccessible within Django templates such as::
    - Methods that are require arguments
    - Methods that have .alters_data = True set. (This is the default for save() and delete() methods of Django ORM instances)
    - Methods or attributes that are private (start with _)
    - Attributes that raise an expception when evaluated.

Example: {% attributes request.user %} -> ['first_name', 'last_name', 'email', set_password', ...]