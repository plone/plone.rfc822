Supermodel handler
==================

This package contains a handler for the ``marshal`` ``plone.supermodel``
namespace, which can be used to mark the primary field of a schema.

This handler is installed so long as ``plone.supermodel`` is installed.

First, let's load this package's ZCML so that we can run the tests:

    >>> configuration = b"""\
    ... <configure xmlns="http://namespaces.zope.org/zope">
    ...
    ...     <include package="zope.component" file="meta.zcml" />
    ...     <include package="plone.supermodel" />
    ...     <include package="plone.rfc822" />
    ...
    ... </configure>
    ... """
    >>> from io import BytesIO
    >>> from zope.configuration import xmlconfig
    >>> xmlconfig.xmlconfig(BytesIO(configuration))

Next, let's define a sample model that exercises the 'marshal' attribute.

    >>> schema = """\
    ... <?xml version="1.0" encoding="UTF-8"?>
    ... <model xmlns="http://namespaces.plone.org/supermodel/schema"
    ...        xmlns:marshal="http://namespaces.plone.org/supermodel/marshal">
    ...     <schema>
    ...         <field type="zope.schema.TextLine" name="title">
    ...             <title>title</title>
    ...         </field>
    ...         <field type="zope.schema.Text" name="body" marshal:primary="true">
    ...             <title>Body</title>
    ...         </field>
    ...     </schema>
    ... </model>
    ... """

We can load this using plone.supermodel:

    >>> from plone.supermodel import loadString
    >>> model = loadString(schema)

The ``body`` field should now be marked with the ``IPrimaryField`` marker:

    >>> from plone.rfc822.interfaces import IPrimaryField
    >>> schema = model.schema
    >>> IPrimaryField.providedBy(schema['title'])
    False
    >>> IPrimaryField.providedBy(schema['body'])
    True

Naturally, we can also write out the primary field attribute from an interface
on which it is marked:

    >>> from zope.interface import Interface, alsoProvides
    >>> from zope import schema
    >>> class ITestSchema(Interface):
    ...     title = schema.TextLine(title=u"Title")
    ...     body = schema.Text(title=u"Body")
    >>> alsoProvides(ITestSchema['body'], IPrimaryField)

    >>> from plone.supermodel import serializeSchema
    >>> print(serializeSchema(ITestSchema))  # doctest: +NORMALIZE_WHITESPACE
    <model xmlns:i18n="http://xml.zope.org/namespaces/i18n" xmlns:marshal="http://namespaces.plone.org/supermodel/marshal" xmlns="http://namespaces.plone.org/supermodel/schema">
      <schema based-on="zope.interface.Interface">
        <field name="title" type="zope.schema.TextLine">
          <title>Title</title>
        </field>
        <field name="body" type="zope.schema.Text" marshal:primary="true">
          <title>Body</title>
        </field>
      </schema>
    </model>
