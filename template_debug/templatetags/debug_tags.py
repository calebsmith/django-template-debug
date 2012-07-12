"""
Template tags that aid in common debugging scenarios.
"""

try:
    import ipdb as pdb
except ImportError:
    import pdb
from pprint import pprint
from collections import Iterable

from django.conf import settings
from django import template


register = template.Library()
TEMPLATE_DEBUG = getattr(settings, 'TEMPLATE_DEBUG', False)


def _flatten(iterable):
    for i in iterable:
        if isinstance(i, Iterable) and not isinstance(i, basestring):
            for sub_i in _flatten(i):
                yield sub_i
        else:
            yield i


@register.simple_tag(takes_context=True)
def variables(context):
    if not TEMPLATE_DEBUG:
        return []
    availables = set(_flatten((dicts.keys() for dicts in context.dicts)))
    availables.remove('block')
    availables = sorted(list(availables))
    pprint(availables)
    return availables


@register.simple_tag(takes_context=True)
def set_trace(context):
    """
    Start a pdb set_trace inside of the template with the context available as
    'context'. Uses ipdb if available.
    """
    if TEMPLATE_DEBUG:
        print("For best results, pip install ipdb")
        print("Variables that are available in the current context:")
        availables = variables(context)
        print('Use `availables` to show this list. Use ' \
              '`context.variable_name to access variables in the context')
        for var in availables:
            setattr(context, var, context[var])
        pdb.set_trace()


@register.simple_tag
def details(var):
    """
    Prints a dictionary showing the attributes of a variable, and if possible, 
    their corresponding values.
    """
    if TEMPLATE_DEBUG:
        module = getattr(var, '__module__', '')
        kls = getattr(getattr(var, '__class__', ''), '__name__', '')
        if module:
            print('Module: {0}'.format(module))
        if kls:
            print('Class: {0}'.format(kls))
        attrs = (attr for attr in dir(var) if not attr.startswith('_'))
        var_data = {}
        for attr in attrs:
            try:
                value = getattr(var, attr)
            except:
                pass
            else:
                var_data[attr] = value
        pprint(var_data)
