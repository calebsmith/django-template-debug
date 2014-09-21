.. _set_trace:

=========
Set Trace
=========

Syntax: {% set_trace %}

Behavior:
    - Starts a set_trace while the template is being rendered. ipdb is used if available; otherwise pdb is used as a fallback.
    - The context is available inside of the set_trace as `context`.
    - The context variables are available in the local scope as the key provided in the context dictionary. (e.g. If a variable 'items' is in the context, it is available in the set trace as the variable 'items')


Inside the Debugger
*******************

Once inside the debugger, one can use details, attributes, variables, and render as functions as follows::

    details(variable_name)
    attributes(variable_name)
    variables(context)
    render(string)

The details, attributes, and variables functions work the same as their template tag counterparts.  For each
of these, refer to their corresponding pages for more details.

The render function is a quick way to test out how a given template string would be rendered using the
current context. For instance, typing `render('{{ now }}')` in a set trace will display the rendered string,
pulling the variable `now` from the current context.

Usages and Examples
*******************

A common use case is to put a {% set_trace %} near the top of the template you want to debug somewhere that you can assure will be executed (e.g. not inside of a conditional or loop). However, other placements can prove fruitful. For example, another possiblity is to put the {% set_trace %} tag inside a for loop and inspect each element one at a time, and iterate using the continue command in the debugger, for example::

    {% for item in items %}
        {% set_trace %}
    {% endfor %}

    Inside of the debugger:
        In: item
        Out: <SomeObject: identifier_1>
        In: item.attribute
        Out: "Deck of Many Things"
        In: c
        In: item
        Out: <SomeObject: identifier_2>
        In: item.attribute
        Out: "Portable Hole"
        In: render('{% if item.magical %}A magical item {% endif %}')
        Out: "A magical item"

Using a similar technique, one might place {% set_trace %} inside of loops or conditional blocks to assure these blocks are or are not being executed given certain criteria. For example, if the given scenario causes the containing conditional to evaluate to true, the runserver will drop into a debugger, otherwise template rendering will continue as normal.
