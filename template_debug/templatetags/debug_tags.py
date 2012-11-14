"""
Template tags that aid in common debugging scenarios.
"""

from __future__ import unicode_literals

try:
    import ipdb as pdb
except ImportError:
    import pdb
from pprint import pprint

from django.conf import settings
from django import template

from template_debug.utils import get_variables, get_details, find_func


register = template.Library()
TEMPLATE_DEBUG = getattr(settings, 'TEMPLATE_DEBUG', False)


def require_template_debug(f):
    """Decorated function is a no-op if TEMPLATE_DEBUG is False"""
    def _(*args, **kwargs):
        return f(*args, **kwargs) if TEMPLATE_DEBUG else None
    return _


def _display_details(var_data):
    """
    Given a dictionary of variable attribute data from get_details display the
    data in the terminal.
    """
    meta_keys = (key for key in list(var_data.keys())
                 if key.startswith('META_'))
    for key in meta_keys:
        display_key = key[5:].capitalize()
        pprint('{0}: {1}'.format(display_key, var_data.pop(key)))
    pprint(var_data)


@require_template_debug
@register.simple_tag(takes_context=True)
def variables(context):
    """
    Given a context, return a flat list of variables available in the context.
    """
    availables = get_variables(context)
    pprint(availables)


@require_template_debug
@register.simple_tag
def details(var):
    """
    Prints a dictionary showing the attributes of a variable, and if possible,
    their corresponding values.
    """
    _display_details(get_details(var))


@require_template_debug
@register.simple_tag
def find(var):
    """
    Given a callable, return a string with the function's name, filename
    (minus PROJECT_ROOT if present), a colon separator and the line number. If the object is not
    callable, return the string "Not a callable"
    """
    func_details = find_func(var)
    return func_details if func_details else 'Not a callable'


@require_template_debug
@register.simple_tag(takes_context=True)
def set_trace(context):
    """
    Start a pdb set_trace inside of the template with the context available as
    'context'. Uses ipdb if available.
    """
    print("For best results, pip install ipdb.")
    print("Variables that are available in the current context:")
    availables = get_variables(context)
    pprint(availables)
    print('Type `availables` to show this list.')
    print('Type <variable_name> to access one.')
    for var in availables:
        locals()[var] = context[var]
    pdb.set_trace()
