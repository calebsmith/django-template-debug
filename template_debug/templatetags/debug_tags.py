"""
Template tags that aid in common debugging scenarios.
"""

from __future__ import unicode_literals

from pprint import pprint

from django.conf import settings
from django import template
import socket

from template_debug.utils import get_variables, get_details, get_attributes

register = template.Library()


def require_template_debug(f):
    """Decorated function is a no-op if TEMPLATE_DEBUG is False"""
    def _(*args, **kwargs):
        TEMPLATE_DEBUG = getattr(settings, 'TEMPLATE_DEBUG', False)
        return f(*args, **kwargs) if TEMPLATE_DEBUG else ''
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
    return availables


@require_template_debug
@register.simple_tag
def attributes(var):
    """
    Given a variable in the template's context, print and return the list of
    attributes thare accessible inside of the template. For example, private
    attributes or callables that require arguments are excluded.
    """
    attrs = get_attributes(var)
    pprint(attrs)
    return attrs


@require_template_debug
@register.simple_tag
def details(var):
    """
    Prints a dictionary showing the attributes of a variable, and if possible,
    their corresponding values.
    """
    var_details = get_details(var)
    _display_details(var_details)
    return var_details


@require_template_debug
@register.simple_tag(takes_context=True)
def set_trace(context):
    """
    Start a pdb set_trace inside of the template with the context available as
    'context'. Uses ipdb if available.
    """
    try:
        import ipdb as pdb
    except ImportError:
        import pdb
        print("For best results, pip install ipdb.")
    print("Variables that are available in the current context:")
    render = lambda s: template.Template(s).render(context)
    availables = get_variables(context)
    pprint(availables)
    print('Type `availables` to show this list.')
    print('Type <variable_name> to access one.')
    print('Use render("template string") to test template rendering')
    # Cram context variables into the local scope
    for var in availables:
        locals()[var] = context[var]
    pdb.set_trace()
    return ''


#cache a socket error when doing pydevd.settrace, to allow running without debugger
pdevd_not_available = False


@require_template_debug
@register.simple_tag(takes_context=True)
def pydevd(context):
    """
    Start a pydev settrace
    """
    global pdevd_not_available
    if pdevd_not_available:
        return ''
    try:
        import pydevd
    except ImportError:
        pdevd_not_available = True
        return ''
    render = lambda s: template.Template(s).render(context)
    availables = get_variables(context)
    for var in availables:
        locals()[var] = context[var]
    #catch the case where no client is listening
    try:
        pydevd.settrace()
    except socket.error:
        pdevd_not_available = True
    return ''
