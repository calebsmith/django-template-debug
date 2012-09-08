from copy import copy

from template_debug.tests.base import TemplateDebugTestCase
from template_debug.utils import _flatten, get_variables, get_details


class FlattenTestCase(TemplateDebugTestCase):
    """TestCase for _flatten"""

    def test_flattens_inner_list(self):
        "Assure arbitrarily nested lists are flattened"
        nested_list = [1, [2, [3, 4, [5], ], 6, 7], 8]
        self.assertEqual(list(_flatten(nested_list)), range(1, 9))

    def test_flattens_tuples(self):
        "Assure nested tuples are also flattened"
        nested_tuples = (1, (2, 3, (4, ), 5), 6)
        self.assertEqual(list(_flatten(nested_tuples)), range(1, 7))

    def test_flattens_sets(self):
        "Assure nested sets are flattened"
        nested_sets = set([1, frozenset([2, 3]), 4])
        self.assertEqual(list(_flatten(nested_sets)), range(1, 5))

    def test_flatten_nested_combinations(self):
        "Assure nested iterables are flattened"
        nested = [1, frozenset([2, 3]), (4, (5,), 6), [7], 8]
        self.assertEqual(list(_flatten(nested)), range(1, 9))

    def test_flatten_generator(self):
        "Assure generators are flattened"
        gens = [1, xrange(2, 4), (num for num in (4, xrange(5, 7)))]
        self.assertEqual(list(_flatten(gens)), range(1, 7))

    def test_flatten_string_unchanged(self):
        "Assure strings are left intact"
        data = ['abc', ['abc', ['abc']], 'abc']
        self.assertEqual(list(_flatten(data)), ['abc', 'abc', 'abc', 'abc'])


class GetVariablesTestCase(TemplateDebugTestCase):
    """TestCase for get_variables"""

    def setUp(self):
        self.context = self.get_context()
        self.globals = [
            'LANGUAGES', 'LANGUAGE_BIDI', 'LANGUAGE_CODE', 'MEDIA_URL',
            'STATIC_URL', 'csrf_token', 'messages', 'params', 'perms',
            'request', 'user'
        ]

    def test_context_processos(self):
        """
        Assure get_variables returns variables from context processors in
        alphabetical order
        """
        self.assertEqual(get_variables(self.context), self.globals)

    def test_view_context(self):
        """
        Assure get_vaiables returns variables from the view as well as the
        context processors
        """
        context = self.get_context(url='/a/')
        expected_context = copy(self.globals)
        expected_context.insert(5, 'a')
        expected_context.remove('params')
        self.assertEqual(get_variables(context), expected_context)


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
