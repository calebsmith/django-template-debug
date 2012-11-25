"Test helper functions and base test cases."
import random
import string

from django.template import RequestContext
from django.contrib.auth.models import User
from django.test import TestCase


class TemplateDebugTestCase(TestCase):
    "Base test case with helpers for template debug tests."

    def get_random_string(self, length=10):
        return ''.join(random.choice(string.ascii_letters)
                       for x in range(length))

    def _get_context(self, request, dict_=None, processors=None):
        return RequestContext(request, dict_, processors=processors)

    def get_context(self, url='/'):
        context = self.client.get(url).context
        try:
            return context[0]
        except KeyError:
            return context

    def create_user(self, **kwargs):
        "Factory method for creating Users."
        defaults = {
            'username': self.get_random_string(),
            'email': '',
            'password': self.get_random_string(),
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)
