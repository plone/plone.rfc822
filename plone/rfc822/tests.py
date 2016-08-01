# -*- coding: utf-8 -*-
from plone.testing import layered
from plone.testing.zca import UNIT_TESTING

import doctest
import unittest


DOCFILES = [
    'message.txt',
    'fields.txt',
    'supermodel.txt',
]

optionflags = doctest.ELLIPSIS


def test_suite():

    suite = unittest.TestSuite()
    suite.addTests([
        layered(
            doctest.DocFileSuite(
                docfile,
                optionflags=optionflags,
            ),
            layer=UNIT_TESTING
        )
        for docfile in DOCFILES
    ])
    return suite
