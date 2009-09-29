"""Default field marshalers for the fields in zope.schema.

Note that none of the marshalers will return a value for getContentType(),
because none of the standard field types maintain this information.

These field implement IFromUnicode and are supported by a single marshaler:

* Text, TextLine, Password - store unicode
* Bytes, BytesLine, ASCII, ASCIILine, URI, Id, DottedName - store str
* Bool - stores bool (incorrectly omits IFromUnicode specification)
* Int - stores int, long
* Float - stores float
* Choice - string/unicode values supported

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

import datetime
import dateutil.parser

from zope.component import queryMultiAdapter

from zope.interface import implements, Interface
from zope.component import adapts

from zope.schema.interfaces import IFromUnicode
from zope.schema.interfaces import IBytes
from zope.schema.interfaces import IDatetime, IDate, ITimedelta
from zope.schema.interfaces import ICollection

from plone.rfc822.interfaces import IFieldMarshaler

_marker = object()

class BasefieldMarshaler(object):
    """Base class for field marshalers
    """
    
    implements(IFieldMarshaler)
    
    ascii = False
    
    def __init__(self, context, field):
        self.context = context
        self.field = field.bind(context)
        
        self.instance = context
        if field.interface is not None:
            self.instance = field.interface(context, context)
    
    def marshal(self, charset='utf-8', primary=False):
        value = self._query(_marker)
        if value is _marker:
            return None
        return self.encode(value, charset, primary)
    
    def demarshal(self, value, charset='utf-8', contentType=None, primary=False):
        self._set(self.extract(value, charset, contentType, primary))
    
    def encode(self, value, charset='utf-8', primary=False):
        return None
    
    def extract(self, value, charset='utf-8', contentType=None, primary=False):
        raise ValueError("Demarshalling not implemented for %s" % repr(self.field))
    
    def getContentType(self):
        return None
    
    def getContentLength(self):
        value = self.marshal()
        if value is None:
            return None
        return len(value)
    
    # Helper methods
    
    def _query(self, default=None):
        return self.field.query(self.instance, default)
    
    def _set(self, value):
        try:
            self.field.set(self.instance, value)
        except TypeError, e:
            raise ValueError(e)

class UnicodeFieldMarshaler(BasefieldMarshaler):
    """Default marshaler for fields that support IFromUnicode
    """
    
    adapts(Interface, IFromUnicode)
    
    def encode(self, value, charset='utf-8', primary=False):
        if value is None:
            return None
        return unicode(value).encode(charset)
    
    def extract(self, value, charset='utf-8', contentType=None, primary=False):
        unicodeValue = value.decode(charset)
        try:
            return self.field.fromUnicode(unicodeValue)
        except Exception, e:
            raise ValueError(e)

class ASCIISafeFieldMarshaler(UnicodeFieldMarshaler):
    """Default marshaler for fields that are ASCII safe, but still support
    IFromUnicode. This includes Int, Float and Bool.
    """
    
    ascii = True
    
class BytesFieldMarshaler(BasefieldMarshaler):
    """Default marshaler for IBytes fields and children. These store str
    objects, so we will attempt to encode them directly.
    """
    
    adapts(Interface, IBytes)
    
    ascii = True
    
    def encode(self, value, charset='utf-8', primary=False):
        return value
    
    def extract(self, value, charset='utf-8', contentType=None, primary=False):
        return value

class DatetimeMarshaler(BasefieldMarshaler):
    """Marshaler for Python datetime values
    """
    
    adapts(Interface, IDatetime)
    
    ascii = True
    
    def encode(self, value, charset='utf-8', primary=False):
        if value is None:
            return None
        return value.isoformat()
    
    def extract(self, value, charset='utf-8', contentType=None, primary=False):
        unicodeValue = value.decode(charset)
        try:
            return dateutil.parser.parse(unicodeValue)
        except Exception, e:
            raise ValueError(e)

class DateMarshaler(BasefieldMarshaler):
    """Marshaler for Python date values.
    
    Note: we don't use the date formatting support in the 'email' module as
    this does not seem to be capable of round-tripping values with time zone
    information.
    """
    
    adapts(Interface, IDate)
    
    ascii = True
    
    def encode(self, value, charset='utf-8', primary=False):
        if value is None:
            return None
        return value.isoformat()
    
    def extract(self, value, charset='utf-8', contentType=None, primary=False):
        unicodeValue = value.decode(charset)
        try:
            return dateutil.parser.parse(unicodeValue).date()
        except Exception, e:
            raise ValueError(e)

class TimedeltaMarshaler(BasefieldMarshaler):
    """Marshaler for Python timedelta values
    
    Note: we don't use the date formatting support in the 'email' module as
    this does not seem to be capable of round-tripping values with time zone
    information.
    """
    
    adapts(Interface, ITimedelta)
    
    ascii = True
    
    def encode(self, value, charset='utf-8', primary=False):
        if value is None:
            return None
        return "%d:%d:%d" % (value.days, value.seconds, value.microseconds)
    
    def extract(self, value, charset='utf-8', contentType=None, primary=False):
        unicodeValue = value.decode(charset)
        try:
            days, seconds, microseconds = [int(v) for v in value.split(":")]
            return datetime.timedelta(days, seconds, microseconds)
        except Exception, e:
            raise ValueError(e)

class CollectionMarshaler(BasefieldMarshaler):
    """Marshaler for collection values
    """
    
    adapts(Interface, ICollection)

    @property
    def ascii(self):
        valueTypeMarshaler = queryMultiAdapter((self.context, self.field.value_type,), IFieldMarshaler)
        if valueTypeMarshaler is None:
            return False
        return valueTypeMarshaler.ascii

    def encode(self, value, charset='utf-8', primary=False):
        if value is None:
            return None
        
        valueTypeMarshaler = queryMultiAdapter((self.context, self.field.value_type,), IFieldMarshaler)
        if valueTypeMarshaler is None:
            return None
        
        value_lines = []
        for item in value:
            marshaledValue = valueTypeMarshaler.encode(item, charset=charset, primary=primary)
            if marshaledValue is None:
                marshaledValue = ''
            value_lines.append(marshaledValue)
        
        return '||'.join(value_lines)
    
    def extract(self, value, charset='utf-8', contentType=None, primary=False):
        valueTypeMarshaler = queryMultiAdapter((self.context, self.field.value_type,), IFieldMarshaler)
        if valueTypeMarshaler is None:
            raise ValueError("Cannot demarshal value type %s" % repr(self.field.value_type))
        
        listValue = []
        
        for line in value.split('||'):
            listValue.append(valueTypeMarshaler.extract(line, charset, contentType, primary))
            
        sequenceType = self.field._type
        if isinstance(sequenceType, (list, tuple,)):
            sequenceType = sequenceType[-1]
        
        return sequenceType(listValue)
