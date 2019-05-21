# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

import os


version = '2.0.1'

setup(
    name='plone.rfc822',
    version=version,
    description="RFC822 marshalling for zope.schema fields",
    long_description=(
        open("README.rst").read() + "\n" +
        open("CHANGES.rst").read() + "\n" +
        open(os.path.join("plone", "rfc822", "message.rst")).read()),
    # Get more strings from
    # https://pypi.org/classifiers/
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 5.2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
    ],
    keywords='zope schema rfc822',
    author='Martin Aspeli and contributors',
    author_email='optilude@gmail.com',
    url='https://pypi.org/project/plone.rfc822',
    license='BSD',
    packages=find_packages(),
    namespace_packages=['plone'],
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'supermodel': ['plone.supermodel'],
        'test': ['plone.testing', 'plone.supermodel'],
    },
    install_requires=[
        'python-dateutil',
        'setuptools',
        'zope.component',
        'zope.deprecation',
        'zope.interface',
        'zope.schema',
    ],
    entry_points="""
    """,
)
