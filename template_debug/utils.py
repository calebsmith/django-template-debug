from __future__ import unicode_literals
from functools import partial
from collections import Iterable
from inspect import getargspec, isroutine


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
    return sorted(set(_flatten(context.dicts)))


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
    Given a variable and one of its attributes that are available inside of
    a template, return its 'method' if it is a callable, its class name if it
    is a model manager, otherwise return its value
    """
    value = getattr(var, attr)
    # Rename common Django class names
    kls = getattr(getattr(value, '__class__', ''), '__name__', '')
    if kls in ('ManyRelatedManager', 'RelatedManager', 'EmptyManager'):
        return kls
    if callable(value):
        return 'routine'
    return value


def get_attributes(var):
    """
    Given a varaible, return the list of attributes that are available inside
    of a template
    """
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
    if isroutine(value):
        # Remove any routines that are flagged with 'alters_data'
        if getattr(value, 'alters_data', False):
            return False
        else:
            # Remove any routines that require arguments
            try:
                argspec = getargspec(value)
                num_args = len(argspec.args) if argspec.args else 0
                num_defaults = len(argspec.defaults) if argspec.defaults else 0
                if num_args - num_defaults > 1:
                    return False
            except TypeError:
                # C extension callables are routines, but getargspec fails with
                # a TypeError when these are passed.
                pass
    return True
