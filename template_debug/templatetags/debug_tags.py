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
PROJECT_ROOT = getattr(settings, 'PROJECT_ROOT')


def _flatten(iterable):
    """Given an iterable with nested iterables, generate a flat iterable"""
    for i in iterable:
        if isinstance(i, Iterable) and not isinstance(i, basestring):
            for sub_i in _flatten(i):
                yield sub_i
        else:
            yield i


def _get_variables(context):
    """
    Given a context, return a sorted list of varaible names in the context
    """
    if not TEMPLATE_DEBUG:
        return []
    availables = set(_flatten((dicts.keys() for dicts in context.dicts)))
    try:
        availables.remove('block')
    except KeyError:
        pass
    return sorted(list(availables))


def _get_detail_data(var):
    """
    Given a variable inside the context, obtain the attributes/callables,
    their values where possible, and the module name and class name if possible
    """
    var_data = {}
    # Obtain module and class details if available and add them in
    module = getattr(var, '__module__', '')
    kls = getattr(getattr(var, '__class__', ''), '__name__', '')
    if module:
        var_data['META_module name'] = module
    if kls:
        var_data['META_class name'] = kls
    for attr in dir(var):
        value = _get_detail_value(var, attr)
        if value is not None:
            var_data[attr] = value
    return var_data


def _get_detail_value(var, attr):
    """
    Given a variable and one of its attributes, return its value. Return None
    if var.attribute raises an exception, is private (starts with _), or is
    a callable that is flagged with alters_data. Callables and Django ORM
    objects return as strings.
    """
    # Remove private methods
    if attr.startswith('_'):
        return None
    try:
        value = getattr(var, attr)
    except:
        return None
    else:
        if callable(value):
            # Remove methods that alter data
            if getattr(value, 'alters_data', False):
                return None
            else:
                # Remove methods that require arguments
                if hasattr(value, 'im_func'):
                    if value.im_func.func_code.co_argcount > 1:
                        return None
                return 'method'
        # Rename common Django class names
        kls = getattr(getattr(value, '__class__', ''), '__name__', '')
        if kls in ('ManyRelatedManager', 'RelatedManager'):
            value = kls
        return value


def _display_details(var_data):
    meta_keys = (key for key in list(var_data.keys())
                 if key.startswith('META_'))
    for key in meta_keys:
        display_key = key[5:].capitalize()
        pprint('{0}: {1}'.format(display_key, var_data.pop(key)))
    pprint(var_data)


@register.simple_tag(takes_context=True)
def variables(context):
    availables = _get_variables(context)
    if TEMPLATE_DEBUG:
        pprint(availables)
    return availables


@register.simple_tag
def details(var):
    """
    Prints a dictionary showing the attributes of a variable, and if possible,
    their corresponding values.
    """
    if TEMPLATE_DEBUG:
        _display_details(_get_detail_data(var))


@register.simple_tag
def find(var):
    """
    Given a callable, return a string with the filename (minus PROJECT_ROOT if
    present), a colon separator and the line number. If the object is not
    callable returns the string "Not a callable"
    """
    if TEMPLATE_DEBUG:
        if callable(var):
            func_code = var.im_func.func_code
            filename = func_code.co_filename
            filename = filename.lstrip(PROJECT_ROOT)
            lineno = unicode(func_code.co_firstlineno)
            result = u':'.join((filename, lineno))
        else:
            result = u'Not a callable'
        return result


@register.simple_tag(takes_context=True)
def set_trace(context):
    """
    Start a pdb set_trace inside of the template with the context available as
    'context'. Uses ipdb if available.
    """
    if TEMPLATE_DEBUG:
        print("For best results, pip install ipdb.")
        print("Variables that are available in the current context:")
        availables = _get_variables(context)
        pprint(availables)
        print('Type `availables` to show this list.')
        print('Type <variable_name> to access one.')
        for var in availables:
            locals()[var] = context[var]
        pdb.set_trace()
