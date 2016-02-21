from setuptools import setup, find_packages
import os

version = '1.1.2.dev0'

setup(
    name='plone.rfc822',
    version=version,
    description="RFC822 marshalling for zope.schema fields",
    long_description=(
        open("README.rst").read() + "\n" +
        open("CHANGES.rst").read() +
        open(os.path.join("plone", "rfc822", "message.txt")).read()),
    # Get more strings from
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
    ],
    keywords='zope schema rfc822',
    author='Martin Aspeli',
    author_email='optilude@gmail.com',
    url='https://pypi.python.org/pypi/plone.rfc822',
    license='BSD',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['plone'],
    include_package_data=True,
    zip_safe=False,
    extras_require={
      'supermodel': ['plone.supermodel'],
      'test': ['plone.testing'],
    },
    install_requires=[
        'setuptools',
        'zope.schema',
        'zope.component',
        'zope.interface',
        'python-dateutil',
    ],
    entry_points="""
    """,
    )
