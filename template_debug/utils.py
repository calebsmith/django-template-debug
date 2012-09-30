from collections import Iterable

from django.conf import settings

PROJECT_ROOT = getattr(settings, 'PROJECT_ROOT', '')


def _flatten(iterable):
    """Given an iterable with nested iterables, generate a flat iterable"""
    for i in iterable:
        if isinstance(i, Iterable) and not isinstance(i, basestring):
            for sub_i in _flatten(i):
                yield sub_i
        else:
            yield i


def get_variables(context):
    """
    Given a context, return a sorted list of variable names in the context
    """
    availables = set(_flatten((dicts.keys() for dicts in context.dicts)))
    # Don't show the rendering tree 'block' as a variable in the context
    try:
        availables.remove('block')
    except KeyError:
        pass
    return sorted(list(availables))


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
    managers return as strings indicating 'method' or another friendly name.
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


def find_func(var):
    im_func = _find_func_im_func(var)
    try:
        original_name = im_func.func_name
    except AttributeError:
        return None
    func_closures = _flatten(_find_func_or_closures(var))
    for func in filter(lambda x: x, func_closures):
        funcname = func.split(':')[0]
        if funcname == original_name:
            return func
    # If original name couldn't be found, return a best guess
    return func


def _find_func_im_func(var):
    """
    Given a variable, return im_func if available, otherwise return the
    variable
    """
    return getattr(var, 'im_func', var)


def _find_func_or_closures(var):
    """
    Given a callable, return a list of strings that are : delimited and
    represent function meta data in the format: "name:filename:line_number".
    If the argument is not callable return [None]. A callable with closures
    returns a list of meta data strings such as:
        [name:filename:line_number, ...]
    """
    if callable(var):
        im_func = _find_func_im_func(var)
        closures = im_func.func_closure
        if closures:
            return _find_closures(closures)
        else:
            return _find_func_details(im_func)
    else:
        return [None]


def _find_func_details(im_func):
    """
    Given a function's im_func return : delimited string of the function's
    name, filename, and line number.
    """
    func_code = im_func.func_code
    filename = func_code.co_filename
    funcname = im_func.func_name
    filename = filename.lstrip(PROJECT_ROOT)
    lineno = unicode(func_code.co_firstlineno)
    return [':'.join((funcname, filename, lineno))]


def _find_closures(closures):
    results = []
    for closure in closures:
        contents = closure.cell_contents
        if isinstance(contents, Iterable):
            for content in contents:
                results.append(_find_func_or_closures(content))
        else:
            results.append(_find_func_or_closures(contents))
    return results
