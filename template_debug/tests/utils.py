from copy import copy

from template_debug.tests.base import TemplateDebugTestCase
from template_debug.utils import _flatten, get_variables


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
