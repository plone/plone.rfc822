# -*- coding: utf-8 -*-
from plone.rfc822._utils import constructMessage
from plone.rfc822._utils import constructMessageFromSchema
from plone.rfc822._utils import constructMessageFromSchemata
from plone.rfc822._utils import initializeObject
from plone.rfc822._utils import initializeObjectFromSchema
from plone.rfc822._utils import initializeObjectFromSchemata
from plone.rfc822._utils import renderMessage
from plone.rfc822.interfaces import IMessageAPI

import zope.interface


zope.interface.moduleProvides(IMessageAPI)
