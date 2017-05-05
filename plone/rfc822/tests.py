# -*- coding: utf-8 -*-
from plone.testing import layered
from plone.testing.zca import UNIT_TESTING

import doctest
import unittest
import re
import sys


DOCFILES = [
    'message.rst',
    'fields.rst',
    'supermodel.rst',
]

optionflags = doctest.ELLIPSIS | doctest.REPORT_UDIFF | doctest.NORMALIZE_WHITESPACE  # noqa: E501


class Py23DocChecker(doctest.OutputChecker):
    def check_output(self, want, got, optionflags):
        if sys.version_info[0] > 2:
            want = re.sub("u'(.*?)'", "'\\1'", want)
            want = re.sub('u"(.*?)"', '"\\1"', want)
        return doctest.OutputChecker.check_output(self, want, got, optionflags)


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
    return suite
