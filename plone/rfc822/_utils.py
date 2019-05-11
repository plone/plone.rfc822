# -*- coding: utf-8 -*-
"""Implementation of IMessageAPI methods.

import these from plone.rfc822 directly, not from this module.

See interfaces.py for details.
"""
from email.encoders import encode_base64
from email.header import decode_header
from email.header import Header
from email.message import Message
from plone.rfc822.interfaces import IFieldMarshaler
from plone.rfc822.interfaces import IPrimaryField
from zope.component import queryMultiAdapter
from zope.deprecation import deprecate
from zope.schema import getFieldsInOrder

import logging
import six


logger = logging.getLogger("plone.rfc822")


def safe_native_string(value, encoding='utf8'):
    ''' Try to convert value into a native string
    '''
    if six.PY2:
        if isinstance(value, six.text_type):
            return value.encode(encoding)
    elif isinstance(value, six.binary_type):
        return value.decode(encoding)
    if not isinstance(value, str):
        raise ValueError('Cannot convert %r into a native string' % value)
    return value


def constructMessageFromSchema(context, schema, charset="utf-8"):
    return constructMessage(context, getFieldsInOrder(schema), charset)


def constructMessageFromSchemata(context, schemata, charset="utf-8"):
    fields = []
    for schema in schemata:
        fields.extend(getFieldsInOrder(schema))
    return constructMessage(context, fields, charset)


def _add_payload_to_message(context, msg, primary, charset):
    """If there's a single primary field, we have a non-multipart message with
    a string payload. Otherwise, we return a multipart message

    """
    is_multipart = len(primary) > 1
    if is_multipart:
        msg.set_type("multipart/mixed")

    for name, field in primary:
        if is_multipart:
            payload = Message()
        else:
            payload = msg
        marshaler = queryMultiAdapter((context, field), IFieldMarshaler)
        if marshaler is None:
            continue

        value = marshaler.marshal(charset, primary=True)
        if value is None:
            continue

        content_type = marshaler.getContentType()
        if content_type is not None:
            payload.set_type(content_type)

        charset = marshaler.getCharset(charset)
        if charset is None and not marshaler.ascii:
            # we have real binary data such as images, files, etc.
            # encode to base64!
            payload.set_payload(value)
            encode_base64(payload)
        elif charset is not None:
            # using set_charset() would also add transfer encoding to
            # quoted-printable, which we don't want here.
            # for unicodedata, we keep it as-is, so: binary
            # payload['Content-Transfer-Encoding'] = "BINARY"
            payload.set_param("charset", charset)
            value = safe_native_string(value, charset)
            payload.set_payload(value)
        else:
            value = safe_native_string(value)
            payload.set_payload(value)

        marshaler.postProcessMessage(payload)
        if is_multipart:
            msg.attach(payload)


def constructMessage(context, fields, charset="utf-8"):
    msg = Message()
    primaries = []

    # First get all headers, storing primary fields for later
    for name, field in fields:
        value = ''
        if IPrimaryField.providedBy(field):
            primaries.append((name, field))
            continue
        marshaler = queryMultiAdapter((context, field), IFieldMarshaler)
        if marshaler is None:
            logger.debug(
                "No marshaler found for field {0} of {1}".format(
                    name, repr(context)
                )
            )
            continue
        try:
            value = marshaler.marshal(charset, primary=False)
        except ValueError as e:
            logger.debug(
                "Marshaling of {0} for {1} failed: {2}".format(
                    name, repr(context), str(e)
                )
            )
            continue
        if value is None:
            value = ""
        # Enforce native strings
        value = safe_native_string(value)
        if marshaler.ascii and "\n" not in value:
            msg[name] = value
        else:
            # see https://tools.ietf.org/html/rfc2822#section-3.2.2
            if '\n' in value:
                value = value.replace("\n", r"\n")
            msg[name] = Header(value, charset)

    # Then deal with the primary field
    _add_payload_to_message(context, msg, primaries, charset)

    return msg


@deprecate(
    "Use 'message.as_string()' from 'email.message.Message' class instead."
)
def renderMessage(message, mangleFromHeader=False):
    # to be removed in a 3.x series
    return message.as_string(mangleFromHeader)


def initializeObjectFromSchema(
    context, schema, message, defaultCharset="utf-8"
):
    initializeObject(
        context, getFieldsInOrder(schema), message, defaultCharset
    )


def initializeObjectFromSchemata(
    context, schemata, message, defaultCharset="utf-8"
):
    """Convenience method which calls ``initializeObject()`` with all the
    fields in order, of all the given schemata (a sequence of schema
    interfaces).
    """

    fields = []
    for schema in schemata:
        fields.extend(getFieldsInOrder(schema))
    return initializeObject(context, fields, message, defaultCharset)


def initializeObject(context, fields, message, defaultCharset="utf-8"):
    content_type = message.get_content_type()

    charset = message.get_charset()
    if charset is None:
        charset = message.get_param("charset")
    if charset is not None:
        charset = str(charset)
    else:
        charset = defaultCharset

    header_fields = {}
    primary = []
    for name, field in fields:
        if IPrimaryField.providedBy(field):
            primary.append((name, field))
            continue
        header_fields.setdefault(name.lower(), []).append(field)

    # Demarshal each header
    for name, value in message.items():
        name = name.lower()
        fieldset = header_fields.get(name, None)
        if fieldset is None or len(fieldset) == 0:
            logger.debug("No matching field found for header {0}".format(name))
            continue
        field = fieldset.pop(0)
        marshaler = queryMultiAdapter((context, field), IFieldMarshaler)
        if marshaler is None:
            logger.debug(
                "No marshaler found for field {0} of {1}".format(
                    name, repr(context)
                )
            )
            continue
        header_value, header_charset = decode_header(value)[0]
        if header_charset is None:
            header_charset = charset

        # MIME messages always use CRLF.
        # For headers, we're probably safer with \n
        #
        # Also, replace escaped Newlines, for details see
        # https://tools.ietf.org/html/rfc2822#section-3.2.2
        if isinstance(header_value, six.binary_type):
            header_value = header_value.replace(b"\r\n", b"\n")
            header_value = header_value.replace(b"\\n", b"\n")
        else:
            header_value = header_value.replace("\r\n", "\n")
            header_value = header_value.replace(r"\\n", "\n")
        try:
            marshaler.demarshal(
                header_value,
                message=message,
                charset=header_charset,
                contentType=content_type,
                primary=False,
            )
        except ValueError as e:
            # interface allows demarshal() to raise ValueError to indicate
            # marshalling failed
            logger.debug(
                "Demarshalling of {0} for {1} failed: {2}".format(
                    name, repr(context), str(e)
                )
            )
            continue

    # Then demarshal the primary field(s)
    payloads = message.get_payload()

    # do nothing if we don't have a payload
    if not payloads:
        return

    # A single payload is a string, multiparts are lists
    if isinstance(payloads, six.string_types):
        if len(primary) != 1:
            raise ValueError(
                "Got a single string payload for message, but no primary "
                "fields found for %s" % repr(context)
            )
        payloads = [message]

    if len(payloads) != len(primary):
        raise ValueError(
            "Got %d payloads for message, but %s primary fields "
            "found for %s" % (len(payloads), len(primary), repr(context))
        )
    for idx, payload in enumerate(payloads):
        name, field = primary[idx]
        payload_content_type = payload.get_content_type()
        charset = message.get_charset()
        if charset is not None:
            charset = str(charset)
        else:
            charset = "utf-8"

        marshaler = queryMultiAdapter((context, field), IFieldMarshaler)
        if marshaler is None:
            logger.debug(
                "No marshaler found for primary field {0} of {0}".format(
                    name, repr(context)
                )
            )
            continue
        payload_value = payload.get_payload(decode=True)
        payload_charset = payload.get_content_charset(charset)
        try:
            marshaler.demarshal(
                payload_value,
                message=payload,
                charset=payload_charset,
                contentType=payload_content_type,
                primary=True,
            )
        except ValueError as e:
            # interface allows demarshal() to raise ValueError to
            # indicate marshalling failed
            logger.debug(
                "Demarshalling of {0} for {1} failed: {2}".format(
                    name, repr(context), str(e)
                )
            )
            continue
