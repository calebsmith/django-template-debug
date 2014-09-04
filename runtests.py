#!/usr/bin/env python
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

if hasattr(django, 'setup'):
    django.setup()

if not settings.configured:
    PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'template_debug',
            'example',
        ),
        SITE_ID=1,
        TEMPLATE_DIRS = (
            os.path.join(PROJECT_PATH, 'example', 'templates'),
        ),
        TEMPLATE_LOADERS = (
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        )
    )


def runtests():
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=True, failfast=False)
    failures = test_runner.run_tests(['template_debug', ])
    sys.exit(failures)


if __name__ == '__main__':
    runtests()
