#! /usr/bin/python
import os
from setuptools import setup, find_packages


def read_file(filename):
    """Read a file into a string"""
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    try:
        return open(filepath).read()
    except IOError:
        return ''


setup(
    name='django-template-debug',
    version=__import__('template_debug').__version__,
    author='Caleb Smith',
    author_email='caleb.smithnc@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/calebsmith/django-template-debug',
    license='BSD',
    description=' '.join(__import__('template_debug').__doc__.splitlines()).strip(),
    classifiers=[
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Environment :: Web Environment'
    ],
    long_description=read_file('README.rst'),
)
