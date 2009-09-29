from setuptools import setup, find_packages
import os

version = '1.0a1'

setup(name='plone.rfc822',
      version=version,
      description="RFC822 marshalling for zope.schema fields",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read() +
                       open(os.path.join("plone", "rfc822", "message.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zope schema rfc822',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='http://pypi.python.org/pypi/plone.rfc822',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.schema',
          'zope.component',
          'zope.interface',
          'pytz',
          'python-dateutil',
      ],
      entry_points="""
      """,
      )
