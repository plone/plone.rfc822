from plone.rfc822._utils import safe_native_string
from plone.testing import layered
from plone.testing.zca import UNIT_TESTING

import doctest
import unittest


DOCFILES = [
    "message.rst",
    "fields.rst",
    "supermodel.rst",
]

optionflags = (
    doctest.ELLIPSIS
    | doctest.REPORT_UDIFF
    | doctest.NORMALIZE_WHITESPACE
    | doctest.REPORT_ONLY_FIRST_FAILURE
)


class TestUtils(unittest.TestCase):
    def test_safe_native_string(self):
        self.assertIsInstance(safe_native_string(b""), str)
        self.assertIsInstance(safe_native_string(""), str)
        self.assertRaises(ValueError, safe_native_string, None)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(
        [
            layered(
                doctest.DocFileSuite(
                    docfile,
                    optionflags=optionflags,
                ),
                layer=UNIT_TESTING,
            )
            for docfile in DOCFILES
        ]
    )
    suite.addTest(TestUtils("test_safe_native_string"))
    return suite
