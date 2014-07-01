#!/usr/bin/env python
"""
    vim_fanfou.vim_fanfou_unittest:
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    The vim fanfou unit tests

    :copyright: (c) 2014 by xiong-jia.le ( lexiongjia@gmail.com )
    :license: Vim license. See :help license
"""

import unittest
from . import misc

class TestMsgConv(unittest.TestCase):
    def test_parse_html_str(self):
        self.assertEqual(misc.MSG_CONV.FromHTMLStr("&lt; test &gt;"), 
            "< test >");
        self.assertEqual(misc.MSG_CONV.FromHTMLStr(u"abc"), "abc")


def vim_fanfou_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMsgConv)
    unittest.TextTestRunner().run(suite)

