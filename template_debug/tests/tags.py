from django.conf import settings

from template_debug.tests.base import TemplateDebugTestCase
from template_debug.templatetags.debug_tags import require_template_debug


try:
    from django.utils.six import PY3
except ImportError:
    range = xrange
    PY3 = False


@require_template_debug
def test_func():
    return 'test string'


class RequireTemplateDebugTestCase(TemplateDebugTestCase):

    def test_empty_if_template_debug_false(self):
        settings.TEMPLATE_DEBUG = False
        self.assertEqual(test_func(), '')

    def test_unchanged_if_template_debug_true(self):
        settings.TEMPLATE_DEBUG = True
        self.assertEqual(test_func(), 'test string')
