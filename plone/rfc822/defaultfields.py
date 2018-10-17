# -*- coding: utf-8 -*-
"""Default field marshalers for the fields in zope.schema.

Note that none of the marshalers will return a value for getContentType(),
because none of the standard field types maintain this information.

These field implement IFromUnicode and are supported by a single marshaler:

* Text, TextLine, Password - store six.text_type
* Bytes, BytesLine, ASCII, ASCIILine, URI, Id, DottedName - store str
* Bool - stores bool (incorrectly omits IFromUnicode specification)
* Int - stores int, long
* Float - stores float
* Decimal - stores Decimal
* Choice - string/six.text_type values supported

Do not implement IFromUnicode

* Datetime - stores datetime; we use email.utils.formatdate() to format
* Date - stores date; we use email.utils.formatdate() to format
* Timedelta - stores timedelta; we encode as seconds

Sequence fields - supported if their value_type is supported

* Tuple, List, Set, Frozenset


Unsupported by default:

* Object - stores any object
* InterfaceField - stores Interface
* Dict - stores a dict
"""
from plone.rfc822.interfaces import IFieldMarshaler
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import IBytes
from zope.schema.interfaces import ICollection
from zope.schema.interfaces import IDate
from zope.schema.interfaces import IDatetime
from zope.schema.interfaces import IFromUnicode
from zope.schema.interfaces import ITimedelta

import datetime
import dateutil.parser
import six


_marker = object()


@implementer(IFieldMarshaler)
class BaseFieldMarshaler(object):
    """Base class for field marshalers
    """

    ascii = False

    def __init__(self, context, field):
        self.context = context
        self.field = field.bind(context)
        self.instance = context
        if field.interface is not None:
            self.instance = field.interface(context, context)

    def marshal(self, charset='utf-8', primary=False):
        value = self._query(_marker)
        return (
            None if value is _marker else self.encode(value, charset, primary)
        )

    def demarshal(
        self,
        value,
        message=None,
        charset='utf-8',
        contentType=None,
        primary=False,
    ):

        if value:
            fieldValue = self.decode(
                value, message, charset, contentType, primary
            )
        else:
            fieldValue = self.field.missing_value
        self._set(fieldValue)

    def encode(self, value, charset='utf-8', primary=False):
        return None

    def decode(
        self,
        value,
        message=None,
        charset='utf-8',
        contentType=None,
        primary=False,
    ):
        raise ValueError(
            'Demarshalling not implemented for %s' % repr(self.field)
        )

    def getContentType(self):
        return None

    def getCharset(self, default='utf-8'):
        return None

    def postProcessMessage(self, message):
        pass

    # Helper methods

    def _query(self, default=None):
        return self.field.query(self.instance, default)

    def _set(self, value):
        if getattr(self.instance, 'marker', False):
            print(self.field.__name__)
            print(value)
            print('-' * 5)
        try:
            self.field.set(self.instance, value)
        except TypeError as e:
            raise ValueError(e)


@adapter(Interface, IFromUnicode)
class UnicodeFieldMarshaler(BaseFieldMarshaler):
    """Default marshaler for fields that support IFromUnicode
    """

    def encode(self, value, charset='utf-8', primary=False):
        if value is None:
            return
        if isinstance(value, six.binary_type):
            # value already encoded
            return value
        return six.text_type(value).encode(charset)

    def decode(
        self,
        value,
        message=None,
        charset='utf-8',
        contentType=None,
        primary=False,
    ):
        if isinstance(value, six.binary_type):
            unicodeValue = value.decode(charset)
        else:
            unicodeValue = value
        try:
            return self.field.fromUnicode(unicodeValue)
        except Exception as e:
            raise ValueError(e)

    def getCharset(self, default='utf-8'):
        return default


class UnicodeValueFieldMarshaler(UnicodeFieldMarshaler):
    """Default marshaler for fields that contain unicode data and so may be
    ASCII safe.
    """

    def encode(self, value, charset='utf-8', primary=False):
        encoded = super(UnicodeValueFieldMarshaler, self).encode(
            value, charset, primary
        )
        if not encoded or max(six.iterbytes(encoded)) < 128:
            self.ascii = True
        else:
            self.ascii = False
        return encoded


class ASCIISafeFieldMarshaler(UnicodeFieldMarshaler):
    """Default marshaler for fields that are ASCII safe, but still support
    IFromUnicode. This includes Int, Float, Decimal, and Bool.
    """

    ascii = True

    def getCharset(self, default='utf-8'):
        return None


@adapter(Interface, IBytes)
class BytesFieldMarshaler(BaseFieldMarshaler):
    """Default marshaler for IBytes fields and children. These store str
    objects, so we will attempt to encode them directly.
    """

    ascii = True

    def encode(self, value, charset='utf-8', primary=False):
        return value

    def decode(
        self,
        value,
        message=None,
        charset='utf-8',
        contentType=None,
        primary=False,
    ):
        return value


@adapter(Interface, IDatetime)
class DatetimeMarshaler(BaseFieldMarshaler):
    """Marshaler for Python datetime values
    """

    ascii = True

    def encode(self, value, charset='utf-8', primary=False):
        if value is None:
            return None
        return value.isoformat()

    def decode(
        self,
        value,
        message=None,
        charset='utf-8',
        contentType=None,
        primary=False,
    ):
        if isinstance(value, six.binary_type):
            value = value.decode(charset)
        try:
            return dateutil.parser.parse(value)
        except Exception as e:
            raise ValueError(e)


@adapter(Interface, IDate)
class DateMarshaler(BaseFieldMarshaler):
    """Marshaler for Python date values.

    Note: we don't use the date formatting support in the 'email' module as
    this does not seem to be capable of round-tripping values with time zone
    information.
    """

    ascii = True

    def encode(self, value, charset='utf-8', primary=False):
        if value is None:
            return None
        return value.isoformat()

    def decode(
        self,
        value,
        message=None,
        charset='utf-8',
        contentType=None,
        primary=False,
    ):
        unicodeValue = value.decode(charset)
        try:
            return dateutil.parser.parse(unicodeValue).date()
        except Exception as e:
            raise ValueError(e)


@adapter(Interface, ITimedelta)
class TimedeltaMarshaler(BaseFieldMarshaler):
    """Marshaler for Python timedelta values

    Note: we don't use the date formatting support in the 'email' module as
    this does not seem to be capable of round-tripping values with time zone
    information.
    """

    ascii = True

    def encode(self, value, charset='utf-8', primary=False):
        if value is None:
            return None
        return "%d:%d:%d" % (value.days, value.seconds, value.microseconds)

    def decode(
        self,
        value,
        message=None,
        charset='utf-8',
        contentType=None,
        primary=False,
    ):
        try:
            days, seconds, microseconds = [int(v) for v in value.split(":")]
            return datetime.timedelta(days, seconds, microseconds)
        except Exception as e:
            raise ValueError(e)


@adapter(Interface, ICollection)
class CollectionMarshaler(BaseFieldMarshaler):
    """Marshaler for collection values
    """

    ascii = False

    def getCharset(self, default='utf-8'):
        valueTypeMarshaler = queryMultiAdapter(
            (self.context, self.field.value_type), IFieldMarshaler
        )
        if valueTypeMarshaler is None:
            return None
        return valueTypeMarshaler.getCharset(default)

    def encode(self, value, charset='utf-8', primary=False):
        if value is None:
            return None

        valueTypeMarshaler = queryMultiAdapter(
            (self.context, self.field.value_type), IFieldMarshaler
        )
        if valueTypeMarshaler is None:
            return None

        ascii = True
        value_lines = []
        for item in value:
            marshaledValue = valueTypeMarshaler.encode(
                item, charset=charset, primary=primary
            )
            if marshaledValue is None:
                marshaledValue = ''
            value_lines.append(marshaledValue)
            if not valueTypeMarshaler.ascii:
                ascii = False

        self.ascii = ascii
        if value_lines and isinstance(value_lines[0], six.binary_type):
            return b'||'.join(value_lines)
        else:
            return '||'.join(value_lines)

    def decode(
        self,
        value,
        message=None,
        charset='utf-8',
        contentType=None,
        primary=False,
    ):
        valueTypeMarshaler = queryMultiAdapter(
            (self.context, self.field.value_type), IFieldMarshaler
        )
        if valueTypeMarshaler is None:
            raise ValueError(
                'Cannot demarshal value type %s' % repr(self.field.value_type)
            )

        listValue = []
        if isinstance(value, six.binary_type):
            lines = value.split(b'||')
        else:
            lines = value.split('||')
        for line in lines:
            listValue.append(
                valueTypeMarshaler.decode(
                    line, message, charset, contentType, primary
                )
            )

        sequenceType = self.field._type
        if isinstance(sequenceType, (list, tuple)):
            sequenceType = sequenceType[-1]

        return sequenceType(listValue)
