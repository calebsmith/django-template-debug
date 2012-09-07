"Test helper functions and base test cases."
import random
import string

from django.test import TestCase


class TemplateDebugTestCase(TestCase):
    "Base test case with helpers for template debug tests."

    def get_random_string(self, length=10):
        return ''.join(random.choice(string.ascii_letters) for x in range(length))
