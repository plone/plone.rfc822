# -*- coding: utf-8 -*-
from __future__ import unicode_literals
try:
    from plone.supermodel.interfaces import IFieldMetadataHandler
    HAVE_SUPERMODEL = True
except ImportError:
    HAVE_SUPERMODEL = False

if HAVE_SUPERMODEL:

    from plone.rfc822.interfaces import IPrimaryField
    from plone.supermodel.utils import ns
    from zope.interface import alsoProvides
    from zope.interface import implementer

    @implementer(IFieldMetadataHandler)
    class PrimaryFieldMetadataHandler(object):
        """Define the ``marshal`` namespace.

        This lets you write marshal:primary="true" on a field to mark it as
        a primary field.
        """

        namespace = "http://namespaces.plone.org/supermodel/marshal"
        prefix = "marshal"

        def read(self, fieldNode, schema, field):
            primary = fieldNode.get(ns('primary', self.namespace))
            if (
                primary is not None and
                primary.lower() in ("true", "on", "yes", "y", "1")
            ):
                alsoProvides(field, IPrimaryField)

        def write(self, fieldNode, schema, field):
            if IPrimaryField.providedBy(field):
                fieldNode.set(ns('primary', self.namespace), "true")
