#!/usr/bin/env python
"""
    vim_fanfou.misc_unittest
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    The vim fanfou unit tests for vim_fanfou.misc

    :copyright: (c) 2014 by xiong-jia.le ( lexiongjia@gmail.com )
    :license: Vim license. See :help license
"""

import unittest, os
from . import misc

class BaseTests(unittest.TestCase):
    """Testing misc module"""
    def test_parse_html_str(self):
        """Testing misc.MSG_CONV"""
        ret = misc.MSG_CONV.FromHTMLStr("&lt; test &gt;")
        self.assertEqual(ret, "< test >")
        ret = misc.MSG_CONV.FromHTMLStr("&lt; test &gt;")
        self.assertNotEqual(ret, "&lt; test &gt;")
        ret = misc.MSG_CONV.FromHTMLStr(u"abc")
        self.assertEqual(ret, "abc")

    def test_mbstrlen(self):
        """Testing misc.mbstrlen"""
        src_str = "abc"
        self.assertEqual(misc.mbstrlen(src_str), len(src_str))
        src_str = u"abc"
        self.assertEqual(misc.mbstrlen(src_str), len(src_str))

    def test_chk_keys(self):
        """Testing misc.chk_keys"""
        ret = misc.chk_keys(["abc", "def"], ["abc", "def", "123"])
        self.assertEqual(ret, True)
        ret = misc.chk_keys(["456", "789"], ["abc", "def", "123"])
        self.assertEqual(ret, False)

    def test_parse_tm_str(self):
        """Testing misc.parse_tm_str"""
        ret = misc.parse_tm_str("Fri Jun 20 14:00:03 +0000 2014")
        self.assertNotEqual(0, len(ret))

    def test_resolve_usr_filename(self):
        """Testing misc.resolve_usr_filename"""
        ret = misc.resolve_usr_filename("test_file")
        self.assertTrue(os.path.isabs(ret))
        ret = misc.resolve_usr_filename("/tmp/abc")
        self.assertTrue(os.path.isabs(ret))
        self.assertEqual(ret, "/tmp/abc")

