from __future__ import unicode_literals
from functools import partial
from collections import Iterable

from django.conf import settings


try:
    from django.utils.six import PY3, string_types
except ImportError:
    # Django < 1.5. No Python 3 support
    PY3 = False
    string_types = basestring


def _flatten(iterable):
    """
    Given an iterable with nested iterables, generate a flat iterable
    """
    for i in iterable:
        if isinstance(i, Iterable) and not isinstance(i, string_types):
            for sub_i in _flatten(i):
                yield sub_i
        else:
            yield i


def get_variables(context):
    """
    Given a context, return a sorted list of variable names in the context
    """
    variables = set(_flatten(
        (dicts.keys() for dicts in context.dicts)
    ))
    # Don't show the rendering tree 'block' as a variable in the context
    try:
        variables.remove('block')
    except KeyError:
        pass
    return sorted(list(variables))


def get_details(var):
    """
    Given a variable inside the context, obtain the attributes/callables,
    their values where possible, and the module name and class name if possible
    """
    var_data = {}
    # Obtain module and class details if available and add them in
    module = getattr(var, '__module__', '')
    kls = getattr(getattr(var, '__class__', ''), '__name__', '')
    if module:
        var_data['META_module_name'] = module
    if kls:
        var_data['META_class_name'] = kls
    for attr in get_attributes(var):
        value = _get_detail_value(var, attr)
        if value is not None:
            var_data[attr] = value
    return var_data


def _get_detail_value(var, attr):
    """
    Given a variable and one of its attributes, return its value. Return None
    if var.attribute raises an exception, is private (starts with _), or is
    a callable that is flagged with alters_data. Callables and Django ORM
    managers return as strings indicating 'method' or another friendly name.
    """
    value = getattr(var, attr)
    if callable(value):
        return 'method'
    # Rename common Django class names
    kls = getattr(getattr(value, '__class__', ''), '__name__', '')
    if kls in ('ManyRelatedManager', 'RelatedManager'):
        value = kls
    return value


def get_attributes(var):
    is_valid = partial(is_valid_in_template, var)
    return filter(is_valid, dir(var))


def is_valid_in_template(var, attr):
    """
    Given a variable and one of its attributes, determine if the attribute is
    accessible inside of a Django template and return True or False accordingly
    """
    # Remove private variables or methods
    if attr.startswith('_'):
        return False
    # Remove any attributes that raise an acception when read
    try:
        value = getattr(var, attr)
    except:
        return False
    # Remove any callables that are flagged with 'alters_data'
    if callable(value):
        if getattr(value, 'alters_data', False):
            return False
        else:
            # Remove any callables that require arguments
            value_or_im_func = getattr(value, 'im_func', value)
            # FIXME: Python3 compatibility in question wrt checking for
            # argument count of a function
            if hasattr(value_or_im_func, 'func_code'):
                if value_or_im_func.func_code.co_argcount > 1:
                    return False
    return True
