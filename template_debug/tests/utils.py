from functools import wraps

from django.template import RequestContext
from django.test.client import RequestFactory

from template_debug.tests.base import TemplateDebugTestCase
from template_debug.utils import (_flatten, get_variables, get_details,
    find_func, _find_func_im_func, _find_func_or_closures, _find_func_details,
    _find_closures)


try:
    from django.utils.six import PY3
except ImportError:
    range = xrange
    PY3 = False


class FlattenTestCase(TemplateDebugTestCase):
    """TestCase for _flatten"""

    def test_flattens_inner_list(self):
        "Assure arbitrarily nested lists are flattened"
        nested_list = [1, [2, [3, 4, [5], ], 6, 7], 8]
        self.assertEqual(list(_flatten(nested_list)), list(range(1, 9)))

    def test_flattens_tuples(self):
        "Assure nested tuples are also flattened"
        nested_tuples = (1, (2, 3, (4, ), 5), 6)
        self.assertEqual(list(_flatten(nested_tuples)), list(range(1, 7)))

    def test_flattens_sets(self):
        "Assure nested sets are flattened"
        nested_sets = set([1, frozenset([2, 3]), 4])
        self.assertEqual(list(_flatten(nested_sets)), list(range(1, 5)))

    def test_flatten_nested_combinations(self):
        "Assure nested iterables are flattened"
        nested = [1, frozenset([2, 3]), (4, (5,), 6), [7], 8]
        self.assertEqual(list(_flatten(nested)), list(range(1, 9)))

    def test_flatten_generator(self):
        "Assure generators are flattened"
        gens = [1, list(range(2, 4)), (num for num in (4, list(range(5, 7))))]
        self.assertEqual(list(_flatten(gens)), list(range(1, 7)))

    def test_flatten_string_unchanged(self):
        "Assure strings are left intact"
        data = ['abc', ['abc', ['abc']], 'abc']
        self.assertEqual(list(_flatten(data)), ['abc', 'abc', 'abc', 'abc'])


def test_processor(request):
    return {
        'custom_processor_var': 1,
    }


class GetVariablesTestCase(TemplateDebugTestCase):
    """TestCase for get_variables"""

    def setUp(self):
        factory = RequestFactory()
        self.request = factory.get('/foo/')
        self.known_globals = ['request', 'user']

    def _get_context(self, dict_=None, processors=None):
        return RequestContext(self.request, dict_, processors=processors)

    def test_global_context_processors(self):
        """
        Assure get_variables contains known global context processors such as
        request and user
        """
        variables = set(get_variables(self._get_context()))
        self.assertTrue(variables.issuperset(set(self.known_globals)))

    def test_returned_variable(self):
        """
        Assure get_variables returns variables unique to the context
        """
        variables = get_variables(self._get_context({}))
        self.assertTrue('a' not in variables)
        variables = get_variables(self._get_context({'a': 3}))
        self.assertTrue('a' in variables)

    def test_custom_processors(self):
        variables = get_variables(self._get_context({}, processors=[]))
        self.assertTrue('custom_processor_var' not in variables)
        variables = get_variables(self._get_context({}, processors=[test_processor]))
        self.assertTrue('custom_processor_var' in variables)


class GetDetailsTestCase(TemplateDebugTestCase):

    def setUp(self):
        self.user = self.create_user(username='test', password='test')
        self.client.login(username='test', password='test')

    def test_private_hidden(self):
        """Assure private methods aren't shown"""
        user_details = get_details(self.get_context()['user'])
        self.assertTrue(all([not key.startswith('_')
                             for key in user_details.keys()]))

    def test_alters_data_hidden(self):
        """Assure methods that alter data are hidden"""
        user_details = get_details(self.get_context()['user'])

        def alters_data(key):
            "Given key, returns true if user.key.alters_data = True"
            return not hasattr(getattr(self.user, key, None), 'alters_data')
        self.assertTrue(all(map(alters_data, user_details.keys())))

    def test_takes_arguments_hidden(self):
        """Assure methods that take arguments are hidden"""
        user_details = get_details(self.get_context()['user'])
        user_methods = (
            getattr(self.user, key, None)
            for key in user_details.keys()
            if callable(getattr(self.user, key, None))
        )
        for method in user_methods:
            if hasattr(method, 'im_func'):
                self.assertTrue(method.im_func.func_code.co_argcount <= 1)

    def test_invalid_managers_hidden(self):
        """
        Assure managers that aren't accessible from model instances are hidden
        """
        user = self.get_context()['user']
        user_details = get_details(user)
        invalid_managers = []
        for attr in dir(user):
            try:
                getattr(user, attr)
            except:
                invalid_managers.append(attr)
        self.assertTrue(all([not manager in user_details.keys()
                             for manager in invalid_managers]))

    def test_set_value_method(self):
        """Assure methods have their value set to 'method'"""
        user_details = get_details(self.get_context()['user'])
        for key, value in list(user_details.items()):
            if callable(getattr(self.user, key, None)):
                self.assertEqual(value, 'method')

    def test_set_value_managers(self):
        user = self.get_context()['user']
        user_details = get_details(user)
        managers = []
        for key in user_details.keys():
            value = getattr(self.user, key, None)
            kls = getattr(getattr(value, '__class__', ''), '__name__', '')
            if kls in ('ManyRelatedManager', 'RelatedManager'):
                managers.append(key)
        for key, value in user_details.items():
            if key in managers:
                self.assertTrue(value in
                                ('ManyRelatedManager', 'RelatedManager')
                )

    def test_module_and_class_added(self):
        user_details = get_details(self.get_context()['user'])
        self.assertEqual(user_details['META_module_name'],
                         'django.utils.functional')
        self.assertEqual(user_details['META_class_name'], 'User')


"""
Code stubs for testing function introspection utilities.
"""


def test_decorator(f):
    @wraps
    def _(*args, **kwargs):
        return f(*args, **kwargs)
    return _


@test_decorator
def test_wrapped_func():
    return 'result'


def test_func():
    return 'result'


class TestClass:

    def test_method(self):
        pass


class FindFuncImFuncTestCase(TemplateDebugTestCase):

    def test_find_func_im_func_returns_im_func(self):
        """Assure a method (with an im_func) returns the im_func"""
        method = TestClass.test_method
        self.assertEqual(_find_func_im_func(method), method.im_func)

    def test_find_func_im_func_no_im_func(self):
        """Assure function without an im_func returns itself"""
        func = test_func
        self.assertEqual(_find_func_im_func(func), func)


class FindFuncOrClosureTestCase(TemplateDebugTestCase):

    def test_not_callable(self):
        pass

    def test_find_function_no_closures(self):
        pass

    def test_find_function_with_a_decorator(self):
        pass


class FindFuncIntegrationTestCase(TemplateDebugTestCase):

    def test_find_func_details_returns_meta(self):
        """
        Given an im_func, assure find_func_details returns a list of one string
        with name, filename, and line number.
        """

    def test_find_func(self):
        """
        Given a variable, return function meta data if possible. If the
        function has closures, return a best guess based on the function's name
        Integration Test
        """
        pass

    def test_find_closures(self):
        """
        Assure that given an iterable of function closures, an iterable of its
        contents are returned. If the iterable are themselves closures, these
        closures are followed recursively until all contents are appended.
        """
        pass
