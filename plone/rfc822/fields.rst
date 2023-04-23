Field marshaler tests
=====================

This test exercises the various standard field marshalers.

First, we load the package's configuration::

    >>> configuration = b"""\
    ... <configure
    ...      xmlns="http://namespaces.zope.org/zope"
    ...      i18n_domain="plone.rfc822.tests">
    ...
    ...     <include package="zope.component" file="meta.zcml" />
    ...     <include package="zope.annotation" />
    ...
    ...     <include package="plone.rfc822" />
    ...
    ... </configure>
    ... """

    >>> from io import BytesIO
    >>> from zope.configuration import xmlconfig
    >>> xmlconfig.xmlconfig(BytesIO(configuration))

Next, we'll create an interface which contains an instance of every field
we support::

    >>> from zope.interface import Interface
    >>> from zope import schema
    >>> from dateutil.tz import tzoffset
    >>> tz = tzoffset('Europe/Oslo', 3600)

    >>> class ITestContent(Interface):
    ...     _text = schema.Text()
    ...     _text2 = schema.Text()
    ...     _textLine = schema.TextLine()
    ...     _textLine2 = schema.TextLine()
    ...     _password = schema.Password()
    ...     _password2 = schema.Password()
    ...     _bytes = schema.Bytes()
    ...     _bytesLine = schema.BytesLine()
    ...     _ascii = schema.ASCII()
    ...     _asciiLine = schema.ASCIILine()
    ...     _uri = schema.URI()
    ...     _id = schema.Id()
    ...     _dottedName = schema.DottedName()
    ...     _bool = schema.Bool()
    ...     _int = schema.Int()
    ...     _float = schema.Float()
    ...     _decimal = schema.Decimal()
    ...     _choice1 = schema.Choice(values=[u"one", u"two", u"three"])
    ...     _choice2 = schema.Choice(values=["one", "two", "three"])
    ...     _datetime = schema.Datetime()
    ...     _date = schema.Date()
    ...     _timedelta = schema.Timedelta()
    ...     _tuple = schema.Tuple(value_type=schema.TextLine())
    ...     _list = schema.List(value_type=schema.ASCIILine())
    ...     _set = schema.Set(value_type=schema.Bool())
    ...     _frozenset = schema.FrozenSet(value_type=schema.Timedelta())

This interface is implemented by a the following class::

    >>> from decimal import Decimal
    >>> from zope.interface import implementer
    >>> import datetime
    >>> @implementer(ITestContent)
    ... class TestContent(object):
    ...     _text = u"text\xd8"
    ...     _text2 = u"text" # ascii safe
    ...     _textLine = u"textline\xd8"
    ...     _textLine2 = u"textline" # ascii safe
    ...     _password = u"password\xd8"
    ...     _password2 = u"password" # ascii safe
    ...     _bytes = 'bytes'
    ...     _bytesLine = 'bytesline'
    ...     _ascii = u'ascii'
    ...     _asciiLine = u'asciiline'
    ...     _uri = u'http://plone.org'
    ...     _id = u'some.id'
    ...     _dottedName = 'dotted.name'
    ...     _bool = True
    ...     _int = -10
    ...     _float = 0.3
    ...     _decimal = Decimal("5.0")
    ...     _choice1 = u"two"
    ...     _choice2 = 'two'
    ...     _datetime = datetime.datetime(2009, 1, 2, 15, 10, 5, 1, tz)
    ...     _date = datetime.date(2008, 2, 3)
    ...     _timedelta = datetime.timedelta(3, 4, 5)
    ...     _tuple = (u"one\xd8", u"two")
    ...     _list = ['three', 'four']
    ...     _set = set([True, False])
    ...     _frozenset = frozenset([datetime.timedelta(3, 4, 5), datetime.timedelta(5, 4, 3)])

    >>> t = TestContent()

We can now look up the marshaler for each one and test the marshalling and
extraction methods::

    >>> from zope.component import getMultiAdapter
    >>> from plone.rfc822.interfaces import IFieldMarshaler

Notes:

* Unicode \xd8 (capital letter O with stroke) is \xc3\x98 in UTF-8.
* None of the default marshalers support getContentType(), i.e. they all
  return None
* For simplicity, we do not call ``demarshal()`` for each field. For all the
  standard marshalers, this simply sets the value returned by ``extract()``
  using the ``set()`` method on the field instance.

Text
----

::

    >>> marshaler = getMultiAdapter((t, ITestContent['_text']), IFieldMarshaler)
    >>> marshaler.marshal()
    b'text\xc3\x98'
    >>> marshaler.decode(b'text\xc3\x98')
    'text\xd8'
    >>> marshaler.getContentType() is None
    True
    >>> marshaler.getCharset('utf-8')
    'utf-8'
    >>> marshaler.ascii
    False

Text field types and derivatives will return True for the ``ascii`` property
if the field value is within the ascii range::

    >>> marshaler = getMultiAdapter((t, ITestContent['_text2']), IFieldMarshaler)
    >>> marshaler.marshal()
    b'text'
    >>> marshaler.decode(b'text\xc3\x98')
    'text\xd8'
    >>> marshaler.getContentType() is None
    True
    >>> marshaler.getCharset('utf-8')
    'utf-8'
    >>> marshaler.ascii
    True

TextLine
--------

::

    >>> marshaler = getMultiAdapter((t, ITestContent['_textLine']), IFieldMarshaler)
    >>> marshaler.marshal()
    b'textline\xc3\x98'
    >>> marshaler.decode(b'textline\xc3\x98')
    'textline\xd8'
    >>> marshaler.getContentType() is None
    True
    >>> marshaler.getCharset('utf-8')
    'utf-8'
    >>> marshaler.ascii
    False

Text field types and derivatives will return True for the ``ascii`` property
if the field value is within the ascii range.

::

    >>> marshaler = getMultiAdapter((t, ITestContent['_textLine2']), IFieldMarshaler)
    >>> marshaler.marshal()
    b'textline'
    >>> marshaler.decode(b'textline\xc3\x98')
    'textline\xd8'
    >>> marshaler.getContentType() is None
    True
    >>> marshaler.getCharset('utf-8')
    'utf-8'
    >>> marshaler.ascii
    True

Password
--------

::

    >>> marshaler = getMultiAdapter((t, ITestContent['_password']), IFieldMarshaler)
    >>> marshaler.marshal()
    b'password\xc3\x98'
    >>> marshaler.decode(b'password\xc3\x98')
    'password\xd8'
    >>> marshaler.getContentType() is None
    True
    >>> marshaler.getCharset('utf-8')
    'utf-8'
    >>> marshaler.ascii
    False

Text field types and derivatives will return True for the ``ascii`` property
if the field value is within the ascii range.

::

    >>> marshaler = getMultiAdapter((t, ITestContent['_password2']), IFieldMarshaler)
    >>> marshaler.marshal()
    b'password'
    >>> marshaler.decode(b'password\xc3\x98')
    'password\xd8'
    >>> marshaler.getContentType() is None
    True
    >>> marshaler.getCharset('utf-8')
    'utf-8'
    >>> marshaler.ascii
    True

Bytes
-----

::

    >>> marshaler = getMultiAdapter((t, ITestContent['_bytes']), IFieldMarshaler)
    >>> marshaler.marshal()
    'bytes'
    >>> marshaler.decode(b'bytes')
    b'bytes'
    >>> marshaler.getContentType() is None
    True
    >>> marshaler.getCharset('utf-8') is None
    True
    >>> marshaler.ascii
    True

BytesLine
---------

::

    >>> marshaler = getMultiAdapter((t, ITestContent['_bytesLine']), IFieldMarshaler)
    >>> marshaler.marshal()
    'bytesline'
    >>> marshaler.decode(b'bytesline')
    b'bytesline'
    >>> marshaler.getContentType() is None
    True
    >>> marshaler.getCharset('utf-8') is None
    True
    >>> marshaler.ascii
    True

ASCII
-----

This is an ASCII field which is supposed to store text strings.
Note: There is a BytesField which stores b'foo' binary string.

::

    >>> marshaler = getMultiAdapter((t, ITestContent['_ascii']), IFieldMarshaler)
    >>> marshaler.marshal()
    b'ascii'
    >>> marshaler.decode(b'ascii')
    'ascii'
    >>> marshaler.getContentType() is None
    True
    >>> marshaler.getCharset('utf-8') is None
    True
    >>> marshaler.ascii
    True

ASCIILine
---------

::

    >>> marshaler = getMultiAdapter((t, ITestContent['_asciiLine']), IFieldMarshaler)
    >>> marshaler.marshal()
    b'asciiline'
    >>> marshaler.decode(b'asciiline')
    'asciiline'
    >>> marshaler.getContentType() is None
    True
    >>> marshaler.getCharset('utf-8') is None
    True
    >>> marshaler.ascii
    True

URI
---

An URI is in Python 2 based on unicode text, in Python 3 on bytes.

::

    >>> marshaler = getMultiAdapter((t, ITestContent['_uri']), IFieldMarshaler)
    >>> marshaler.marshal()
    b'http://plone.org'
    >>> marshaler.decode(b'http://plone.org')
    'http://plone.org'
    >>> marshaler.getContentType() is None
    True
    >>> expected = 'utf-8'
    >>> marshaler.getCharset('utf-8') == expected
    True
    >>> marshaler.ascii
    True

Id
--

::

    >>> marshaler = getMultiAdapter((t, ITestContent['_id']), IFieldMarshaler)
    >>> marshaler.marshal()
    b'some.id'
    >>> marshaler.decode(b'some.id')
    'some.id'
    >>> marshaler.getContentType() is None
    True
    >>> expected = 'utf-8'
    >>> marshaler.getCharset('utf-8') == expected
    True
    >>> marshaler.ascii
    True

DottedName
----------

::

    >>> marshaler = getMultiAdapter((t, ITestContent['_dottedName']), IFieldMarshaler)
    >>> marshaler.marshal()
    b'dotted.name'
    >>> marshaler.decode(b'dotted.name')
    'dotted.name'
    >>> marshaler.getContentType() is None
    True
    >>> expected = 'utf-8'
    >>> marshaler.getCharset('utf-8') == expected
    True
    >>> marshaler.ascii
    True

Bool
----

::

    >>> marshaler = getMultiAdapter((t, ITestContent['_bool']), IFieldMarshaler)
    >>> marshaler.marshal()
    b'True'
    >>> t._bool = False
    >>> marshaler.marshal()
    b'False'
    >>> t._bool = True
    >>> marshaler.decode(b'True')
    True
    >>> marshaler.decode(b'False')
    False
    >>> marshaler.getContentType() is None
    True
    >>> marshaler.getCharset('utf-8') is None
    True
    >>> marshaler.ascii
    True

Int
---

::

    >>> marshaler = getMultiAdapter((t, ITestContent['_int']), IFieldMarshaler)
    >>> marshaler.marshal()
    b'-10'
    >>> marshaler.decode(b'-10')
    -10
    >>> marshaler.getContentType() is None
    True
    >>> marshaler.getCharset('utf-8') is None
    True
    >>> marshaler.ascii
    True

Float
-----

::

    >>> marshaler = getMultiAdapter((t, ITestContent['_float']), IFieldMarshaler)
    >>> marshaler.marshal()
    b'0.3'
    >>> marshaler.decode(b'0.25')
    0.25
    >>> marshaler.getContentType() is None
    True
    >>> marshaler.getCharset('utf-8') is None
    True
    >>> marshaler.ascii
    True

Decimal
-------

::

    >>> marshaler = getMultiAdapter((t, ITestContent['_decimal']), IFieldMarshaler)
    >>> marshaler.marshal()
    b'5.0'
    >>> marshaler.decode(b'5.0')
    Decimal('5.0')
    >>> marshaler.getContentType() is None
    True
    >>> marshaler.getCharset('utf-8') is None
    True
    >>> marshaler.ascii
    True

Choice
------

::

    >>> marshaler = getMultiAdapter((t, ITestContent['_choice1']), IFieldMarshaler)
    >>> marshaler.marshal()
    b'two'
    >>> marshaler.decode(b'one')
    'one'
    >>> marshaler.getContentType() is None
    True
    >>> marshaler.getCharset('utf-8')
    'utf-8'
    >>> marshaler.ascii
    True

    >>> marshaler = getMultiAdapter((t, ITestContent['_choice2']), IFieldMarshaler)
    >>> marshaler.marshal()
    b'two'
    >>> marshaler.decode(b'three')
    'three'
    >>> marshaler.getContentType() is None
    True
    >>> marshaler.getCharset('utf-8')
    'utf-8'
    >>> marshaler.ascii
    True

Datetime
--------

::

    >>> marshaler = getMultiAdapter((t, ITestContent['_datetime']), IFieldMarshaler)
    >>> marshaler.marshal()
    '2009-01-02T15:10:05.000001+01:00'
    >>> marshaler.decode(b'2009-01-02T15:10:05.000001+01:00')
    datetime.datetime(2009, 1, 2, 15, 10, 5, 1, tzinfo=tzoffset(None, 3600))
    >>> marshaler.getContentType() is None
    True
    >>> marshaler.getCharset('utf-8') is None
    True
    >>> marshaler.ascii
    True

Date
----

::

    >>> marshaler = getMultiAdapter((t, ITestContent['_date']), IFieldMarshaler)
    >>> marshaler.marshal()
    '2008-02-03'
    >>> marshaler.decode(b'2008-02-03')
    datetime.date(2008, 2, 3)
    >>> marshaler.getContentType() is None
    True
    >>> marshaler.getCharset('utf-8') is None
    True
    >>> marshaler.ascii
    True

Timedelta
---------

::

    >>> marshaler = getMultiAdapter((t, ITestContent['_timedelta']), IFieldMarshaler)
    >>> marshaler.marshal()
    '3:4:5'
    >>> marshaler.decode('3:4:5') == datetime.timedelta(3, 4, 5)
    True
    >>> marshaler.getContentType() is None
    True
    >>> marshaler.getCharset('utf-8') is None
    True
    >>> marshaler.ascii
    True

Tuple
-----

::

    >>> marshaler = getMultiAdapter((t, ITestContent['_tuple']), IFieldMarshaler)
    >>> marshaler.marshal()
    b'one\xc3\x98||two'
    >>> marshaler.decode(b'one\xc3\x98||two')
    ('one\xd8', 'two')
    >>> marshaler.getContentType() is None
    True
    >>> marshaler.getCharset('utf-8')
    'utf-8'
    >>> marshaler.ascii
    False

List
----

::

    >>> marshaler = getMultiAdapter((t, ITestContent['_list']), IFieldMarshaler)
    >>> marshaler.marshal()
    b'three||four'
    >>> marshaler.decode(b'three||four')
    ['three', 'four']
    >>> marshaler.getContentType() is None
    True

    ValueType of the list is ASCIILine!
    >>> marshaler.getCharset('utf-8') is None
    True
    >>> marshaler.ascii
    True

Set
---

::

    >>> marshaler = getMultiAdapter((t, ITestContent['_set']), IFieldMarshaler)
    >>> marshaler.marshal() in (b'False||True', b'True||False')
    True
    >>> marshaler.decode(b'True||False') == set([True, False])
    True
    >>> marshaler.getContentType() is None
    True
    >>> marshaler.getCharset('utf-8') is None
    True
    >>> marshaler.ascii
    True

Frozenset
---------

::

    >>> marshaler = getMultiAdapter((t, ITestContent['_frozenset']), IFieldMarshaler)
    >>> marshaler.marshal() in ('3:4:5||5:4:3', '5:4:3||3:4:5')
    True
    >>> marshaler.decode('3:4:5||5:4:3') == frozenset([datetime.timedelta(3, 4, 5), datetime.timedelta(5, 4, 3)])
    True
    >>> marshaler.getContentType() is None
    True
    >>> marshaler.getCharset('utf-8') is None
    True
    >>> marshaler.ascii
    True
