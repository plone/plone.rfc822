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

import time
import datetime

from zope.component import queryMultiAdapter

from email.Utils import parsedate_tz, mktime_tz, formatdate

from zope.interface import implements, Interface
from zope.component import adapts

from zope.schema.interfaces import IFromUnicode
from zope.schema.interfaces import IDatetime, IDate, ITimedelta
from zope.schema.interfaces import ICollection

from plone.rfc822.interfaces import IFieldMarshaler

class BasefieldMarshaler(object):
    """Base class for field marshalers
    """
    
    implements(IFieldMarshaler)
    
    def __init__(self, context, field):
        self.context = context
        self.field = field.bind(context)
        
        self.instance = context
        if field.interface is not None:
            self.instance = field.interface(context, context)
    
    def marshal(self, charset='utf-8', primary=False):
        return None
    
    def demarshal(self, value, charset='utf-8', contentType=None, primary=False):
        self._set(self.extract(value, charset, contentType, primary))
    
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
    
    def marshal(self, charset='utf-8', primary=False):
        value = self._query()
        if value is None:
            return None
        return unicode(value).encode(charset)
    
    def extract(self, value, charset='utf-8', contentType=None, primary=False):
        unicodeValue = value.decode(charset)
        try:
            return self.field.fromUnicode(unicodeValue)
        except Exception, e:
            raise ValueError(e)        

class DatetimeMarshaler(BasefieldMarshaler):
    """Marshaler for Python datetime values
    """
    
    adapts(Interface, IDatetime)
    
    def marshal(self, charset='utf-8', primary=False):
        value = self._query()
        if value is None:
            return None
        timetuple = value.timetuple()
        timestamp = time.mktime(timetuple)
        return formatdate(timestamp)
    
    def extract(self, value, charset='utf-8', contentType=None, primary=False):
        unicodeValue = value.decode(charset)
        timetuple = parsedate_tz(value)
        timestamp = mktime_tz(timetuple)
        return datetime.datetime.fromtimestamp(timestamp)

class DateMarshaler(DatetimeMarshaler):
    """Marshaler for Python date values
    """
    
    adapts(Interface, IDate)

    def extract(self, value, charset='utf-8', contentType=None, primary=False):
        unicodeValue = value.decode(charset)
        timetuple = parsedate_tz(value)
        timestamp = mktime_tz(timetuple)
        return datetime.date.fromtimestamp(timestamp)

class TimedeltaMarshaler(BasefieldMarshaler):
    """Marshaler for Python timedelta values
    """
    
    adapts(Interface, ITimedelta)
    
    def marshal(self, charset='utf-8', primary=False):
        value = self._query()
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

    def marshal(self, charset='utf-8', primary=False):
        value = self._query()
        if value is None:
            return None
        
        valueTypeMarshaler = queryMultiAdapter((self.context, self.field.value_type,), IFieldMarshaler)
        if valueTypeMarshaler is None:
            return None
        
        value_lines = []
        for item in value:
            marshaledValue = valueTypeMarshaler.marshal(charset=charset, primary=primary)
            if marshaledValue is None:
                marshaledValue = ''
            value_lines.append(marshaledValue)
        return '\n'.join(value_lines)
    
    def extract(self, value, charset='utf-8', contentType=None, primary=False):
        valueTypeMarshaler = queryMultiAdapter((self.context, self.field.value_type,), IFieldMarshaler)
        if valueTypeMarshaler is None:
            raise ValueError("Cannot demarshal value type %s" % repr(self.field.value_type))
        
        listValue = []
        
        for line in value.split('\n'):
            listValue.append(valueTypeMarshaler.extract(line, charset, contentType, primary))
            
        sequenceType = self._type
        if isinstance(sequenceType, (list, tuple,)):
            sequenceType = sequenceType[-1]
        return sequenceType(listValue)
