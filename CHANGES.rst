Changelog
=========

1.1.5 (unreleased)
------------------

Breaking changes:

- *add item here*

New features:

- *add item here*

Bug fixes:

- *add item here*


1.1.4 (2018-06-20)
------------------

New features:

- Start basic Python 3 support.
  [pbauer, dhavlik]


1.1.3 (2016-08-09)
------------------

Fixes:

- code cleanup: pep8, isort, utf8 headers et al.
  [jensens]

- Use zope.interface decorator.
  [gforcada]


1.1.2 (2016-02-21)
------------------

Fixes:

- Fix test isolation problem.
  [thet]

- Replace deprecated ``zope.testing.doctest`` import with ``doctest`` module from stdlib.
  [thet]


1.1.1 (2015-03-21)
------------------

- Update test to reflect the change in the representation of the model namespaces by adding the 18n xml namespace.
  [sneridagh]

- Make sure the tests do not fail if messages contain a trailing blank line. This fixes test failures on Ubuntu 14.04.
  [timo]


1.1 (2013-08-14)
----------------

- Branch for Plone 4.2/4.3 compatibility changes.
  [esteele]


1.0.2 (2013-07-28)
------------------

- Marshall collections as ASCII when possible.
  [davisagli]

- Add support for marshalling decimal fields.
  [davisagli]

1.0.1 (2013-01-01)
------------------

1.0 (2011-05-20)
----------------

* Relicensed under the BSD license.
  See http://plone.org/foundation/materials/foundation-resolutions/plone-framework-components-relicensing-policy
  [davisagli]

1.0b2 (2011-02-11)
------------------

* Add IPrimaryFieldInfo to look up primary field information on a content item.

1.0b1 (2009-10-08)
------------------

* Initial release
