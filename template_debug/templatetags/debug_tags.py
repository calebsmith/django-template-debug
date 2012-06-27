"""
Template tags that aid in common debugging scenarios.
"""

try:
    import ipdb as pdb
except ImportError:
    import pdb
from pprint import pprint

from django.conf import settings
from django import template


register = template.Library()
TEMPLATE_DEBUG = getattr(settings, 'TEMPLATE_DEBUG', False)


@register.simple_tag(takes_context=True)
def set_trace(context):
    """
    Start a pdb set_trace inside of the template with the context available as
    'context'. Uses ipdb if available.
    """
    if TEMPLATE_DEBUG:
        pdb.set_trace()


@register.simple_tag
def attributes(var):
    """
    Prints the available attributes of a variable to the console using dir()
    """
    if TEMPLATE_DEBUG:
        pprint(dir(var))


@register.simple_tag
def details(var):
    """
    Prints a dictionary showing the attributes of a variable, and if possible, 
    their corresponding values.
    """
    if TEMPLATE_DEBUG:
        var_data = {
            'module': getattr(var, '__module__', ''),
            'class': getattr(getattr(var, '__class__', ''), '__name__', ''),
        }
        attrs = (attr for attr in dir(var) if not attr.startswith('_'))
        for attr in attrs:
            try:
                value = getattr(var, attr)
            except:
                pass
            else:
                var_data.update({attr: value})
        pprint(var_data)
