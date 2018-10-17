# -*- coding: utf-8 -*-
from plone.rfc822._utils import safe_native_string
from plone.testing import layered
from plone.testing.zca import UNIT_TESTING

import doctest
import re
import six
import unittest


DOCFILES = [
    'message.rst',
    'fields.rst',
    'supermodel.rst',
]

optionflags = doctest.ELLIPSIS | \
    doctest.REPORT_UDIFF | \
    doctest.NORMALIZE_WHITESPACE | \
    doctest.REPORT_ONLY_FIRST_FAILURE


class Py23DocChecker(doctest.OutputChecker):
    def check_output(self, want, got, optionflags):
        if six.PY2:
            got = re.sub("u'(.*?)'", "'\\1'", got)
        if six.PY3:
            got = re.sub("b'(.*?)'", "'\\1'", got)
        return doctest.OutputChecker.check_output(self, want, got, optionflags)


class TestUtils(unittest.TestCase):

    def test_safe_native_string(self):
        self.assertIsInstance(safe_native_string(b''), str)
        self.assertIsInstance(safe_native_string(u''), str)
        self.assertRaises(ValueError, safe_native_string, None)


def test_suite():

    suite = unittest.TestSuite()
    suite.addTests([
        layered(
            doctest.DocFileSuite(
                docfile,
                optionflags=optionflags,
                checker=Py23DocChecker(),
            ),
            layer=UNIT_TESTING
        )
        for docfile in DOCFILES
    ])
    suite.addTest(TestUtils('test_safe_native_string'))
    return suite
