#!/usr/bin/env python
import os
import sys

# Use the example.settings as the default settings module for testing
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example.settings")

import django

# For Django1.7, load everything
if hasattr(django, 'setup'):
    django.setup()

from django.conf import settings
from django.test.utils import get_runner


def runtests():
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=True, failfast=False)
    failures = test_runner.run_tests(['template_debug', ])
    sys.exit(failures)


if __name__ == '__main__':
    runtests()
