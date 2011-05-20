Introduction
============

This package provides primitives for turning content objects described by
``zope.schema`` fields into RFC (2)822 style messages, as managed by the
Python standard library's ``email`` module.

It consists of:

* A marker interface ``IPrimaryField`` which can be used to indicate the
  primary field of a schema. The primary field will be used as the message
  body.
* An interface ``IFieldMarshaler`` which describes marshalers that convert
  to and from strings suitable for encoding into an RFC 2822 style message.
  These are adapters on ``(context, field)``, where ``context`` is the content
  object and ``field`` is the schema field instance.
* Default implementations of ``IFieldMarshaler`` for the standard fields in
  the ``zope.schema`` package.
* Helper methods to construct messages from one or more schemata or a list of
  fields, and to parse a message and update a context object accordingly.

The helper methods are described by ``plone.rfc822.interfaces.IMessageAPI``,
and are importable directly from the ``plone.rfc822`` package::

    def constructMessageFromSchema(context, schema, charset='utf-8'):
        """Convenience method which calls ``constructMessage()`` with all the
        fields, in order, of the given schema interface
        """
    
    def constructMessageFromSchemata(context, schemata, charset='utf-8'):
        """Convenience method which calls ``constructMessage()`` with all the
        fields, in order, of all the given schemata (a sequence of schema
        interfaces).
        """
    
    def constructMessage(context, fields, charset='utf-8'):
        """Helper method to construct a message.
    
        ``context`` is a content object.
    
        ``fields`` is a sequence of (name, field) pairs for the fields which make
        up the message. This can be obtained from zope.schema.getFieldsInOrder,
        for example.
    
        ``charset`` is the message charset.
    
        The message body will be constructed from the primary field, i.e. the
        field which is marked with ``IPrimaryField``. If no such field exists,
        the message will have no body. If multiple fields exist, the message will
        be a multipart message. Otherwise, it will contain a scalar string
        payload.
    
        A field will be ignored if ``(context, field)`` cannot be multi-adapted
        to ``IFieldMarshaler``, or if the ``marshal()`` method returns None.
        """
    
    def renderMessage(message, mangleFromHeader=False):
        """Render a message to a string
        """
        
    def initializeObjectFromSchema(context, schema, message, defaultCharset='utf-8'):
        """Convenience method which calls ``initializeObject()`` with all the
        fields, in order, of the given schema interface
        """
    
    def initializeObjectFromSchemata(context, schemata, message, defaultCharset='utf-8'):
        """Convenience method which calls ``initializeObject()`` with all the
        fields in order, of all the given schemata (a sequence of schema
        interfaces).
        """

    def initializeObject(context, fields, message, defaultCharset='utf-8'):
        """Initialise an object from a message.
    
        ``context`` is the content object to initialise.
    
        ``fields`` is a sequence of (name, field) pairs for the fields which make
        up the message. This can be obtained from zope.schema.getFieldsInOrder,
        for example.
    
        ``message`` is a ``Message`` object.
    
        ``defaultCharset`` is the default character set to use.
    
        If the message is a multipart message, the primary fields will be read
        in order.
        """

The message format used adheres to the following rules:

* All non-primary fields are represented as headers. The header name is taken
  from the field name, and the value is an encoded string as returned by the
  ``marshal()`` method of the appropriate ``IFieldMarshal`` multi-adapter.
* If no ``IFieldMarshaler`` adapter can be found, the header is ignored.
* Similarly, if no fields are found for a given header when parsing a message,
  the header is ignored.
* If there is a single primary field, the message has a string payload, which
  is the marshalled value of the primary field. In this case, the
  ``Content-Type`` header of the message will be obtained from the primary
  field's marshaler.
* If there are multiple primary fields, each is encoded into its own message,
  each with its own ``Content-Type`` header. The outer message will have a
  content type of ``multipart/mixed`` and headers for other fields.
* A ``ValueError`` error is raised if a message is being parsed which has
  more or fewer parts than there are primary fields.
* Duplicate field names are allowed, and will be encoded as duplicate headers.
  When parsing a message, there needs to be one field per header. That is, if
  a message contains two headers with the name 'foo', the list of field name/
  instance pairs passed to the ``initializeObject()`` method should contain
  two pairs with the name 'foo'. The first field will be used for the first
  header value, the second field will be used for the second header value.
  If a third 'foo' header appears, it will be ignored.
* Since message headers are always lowercase, field names will be matched
  case-insensitively when parsing a message.

Supermodel handler
------------------

If ``plone.supermodel`` is installed, this package will register a namespace
handler for the ``marshal`` namespace, with the URI
``http://namespaces.plone.org/supermodel/marshal``. This can be used to mark
a field as the primary field::

    <model xmlns="http://namespaces.plone.org/supermodel/schema"
           xmlns:marshal="http://namespaces.plone.org/supermodel/marshal">
        <schema>
            <field type="zope.schema.Text" name="test" marshal:primary="true">
                <title>Test field</title>
            </field>
        </schema>
    </model>

``plone.supermodel`` may be installed as a dependency using the extra
``[supermodel]``, but this is probably only useful for running the tests. If
the package is not installed, the handler will not be ignored.

License note
------------

This package is released under the BSD license. Contributors, please do not
add dependencies on GPL code.
