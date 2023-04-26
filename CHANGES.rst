Changelog
=========

.. You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst

.. towncrier release notes start

3.0.0 (2023-04-26)
------------------

Breaking changes:


- Remove long deprecated `renderMessage` function.
  [@jensens] (1-1)
- Drop python 2.7 compatibility.
  [gforcada] (#1)


Internal:


- Update configuration files.
  [plone devs] (a864b30f)


2.0.2 (2020-04-22)
------------------

Bug fixes:


- Minor packaging updates. (#1)


2.0.1 (2019-05-21)
------------------

Bug fixes:


- Use a better type check in the payload parser.
  [Rotonen] (#7)


2.0.0 (2018-11-04)
------------------

Breaking changes:

- Deprecate ``renderMessage(message)``,
  use stdlibs ``message.as_string()`` from ``email.message.Message`` class instead.
  [jensens]

- Newline handling in MIME-headers: ``\n`` are now escaped explicit.
  This follows RFC2822 section 3.2.2.
  [jensens]

- Drop support of Python 2.6
  [jensens]

New features:

- ``constructMessage`` now handles base64 encoding automatically for all marshallers,
  where ``marshaler.ascii`` is ``False`` and ``marshaler.getContentType`` is ``None``.
  [jensens]

- Support for Python 3+
  Also big code overhaul included.
  [jensens]


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
