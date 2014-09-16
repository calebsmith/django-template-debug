from django.test.client import RequestFactory

from template_debug.tests.base import TemplateDebugTestCase
from template_debug.utils import (_flatten, get_variables, get_details,
    is_valid_in_template, get_attributes)


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

    def test_global_context_processors(self):
        """
        Assure get_variables contains known global context processors such as
        request and user
        """
        variables = set(get_variables(self._get_context(self.request)))
        self.assertTrue(variables.issuperset(set(self.known_globals)))

    def test_returned_variable(self):
        """
        Assure get_variables returns variables unique to the context
        """
        variables = get_variables(self._get_context(self.request, {}))
        self.assertTrue('a' not in variables)
        variables = get_variables(self._get_context(self.request, {'a': 3}))
        self.assertTrue('a' in variables)

    def test_custom_processors(self):
        variables = get_variables(self._get_context(
            self.request, {}, processors=[])
        )
        self.assertTrue('custom_processor_var' not in variables)
        variables = get_variables(self._get_context(
            self.request, {}, processors=[test_processor])
        )
        self.assertTrue('custom_processor_var' in variables)


class TestClass(object):

    def _private(self):
        return 'private'

    def takes_args(self, x):
        return x

    def alters_data(self):
        return 'data was changed'
    alters_data.alters_data = True

    def valid_method(self):
        return True

    def has_kwargs(self, foobars=None):
        return foobars


class IsValidInTemplateTestCase(TemplateDebugTestCase):

    def setUp(self):
        request = RequestFactory().get('/foo/')
        test_object = TestClass()
        context = self._get_context(request, {'test_object': test_object})
        self.test_object = context['test_object']

    def test_private(self):
        is_valid = is_valid_in_template(self.test_object, '_private')
        self.assertEqual(is_valid, False,
            'is_valid should be false for private methods'
        )

    def test_takes_args(self):
        is_valid = is_valid_in_template(self.test_object, 'takes_args')
        self.assertEqual(is_valid, False,
            'is_valid should be false methods that require arguments'
        )

    def test_alters_data(self):
        is_valid = is_valid_in_template(self.test_object, 'alters_data')
        self.assertEqual(is_valid, False,
            'is_valid should be false for the methods with .alters_data = True'
        )

    def test_valid_method(self):
        is_valid = is_valid_in_template(self.test_object, 'valid_method')
        self.assertEqual(is_valid, True,
            'is_valid should be true for methods that are accessible to templates'
        )

    def test_has_kwargs(self):
        is_valid = is_valid_in_template(self.test_object, 'has_kwargs')
        self.assertEqual(is_valid, True,
            'is_valid should be true for methods that take kwargs'
        )


class GetAttributesTestCase(TemplateDebugTestCase):

    def setUp(self):
        request = RequestFactory().get('/foo/')
        test_object = TestClass()
        context = self._get_context(request, {'test_object': test_object})
        self.test_object = context['test_object']

    def test_valid_list(self):
        valid_attributes = set(get_attributes(self.test_object))
        self.assertEqual(set(['has_kwargs', 'valid_method']), valid_attributes,
            'has_kwargs and valid_method are the only valid routines of TestObject'
        )


class GetDetailsTestCase(TemplateDebugTestCase):

    def setUp(self):
        self.user = self.create_user(username='test', password='test')
        self.client.login(username='test', password='test')

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
        self.assertEqual(user_details['get_full_name'], 'routine')

    def test_set_value_managers(self):
        user = self.get_context()['user']
        user_details = get_details(user)
        managers = []
        for key in user_details.keys():
            value = getattr(self.user, key, None)
            kls = getattr(getattr(value, '__class__', ''), '__name__', '')
            if kls in ('ManyRelatedManager', 'RelatedManager', 'EmptyManager'):
                managers.append(key)
        for key, value in user_details.items():
            if key in managers:
                self.assertTrue(value in
                    ('ManyRelatedManager', 'RelatedManager', 'EmptyManager',)
                )

    def test_module_and_class_added(self):
        user_details = get_details(self.get_context()['user'])
        self.assertEqual(user_details['META_module_name'],
                         'django.utils.functional')
        self.assertEqual(user_details['META_class_name'], 'User')

    def test_get_details_c_extensions(self):
        """
        Ensures get_details works on objects with callables that are
        implemented in C extensions. inspect.getargspec fails with a TypeError
        for such callables, and get_details needs to handle this gracefully

        N.B. Only Python >=2.7 has bit_length C routine on Booleans so the test
        has to be skipped for Python2.6
        """
        if hasattr(True, 'bit_length'):
            try:
                details = get_details(True)
            except TypeError:
                self.fail('Fails to handle C routines for call to inspect.argspec')
            self.assertEqual(details['bit_length'], 'routine')
        user_details = get_details(self.get_context()['user'])
        self.assertTrue(any((
            user_details['META_module_name'], 'django.contrib.auth.models',
            user_details['META_module_name'], 'django.utils.functional'
        )))
        self.assertTrue(any((
            user_details['META_class_name'] == 'User',
            user_details['META_class_name'] == 'AnonymousUser'
        )))
