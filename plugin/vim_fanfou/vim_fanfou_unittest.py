#!/usr/bin/env python
"""
    vim_fanfou.vim_fanfou_unittest:
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    The entry of all unit tests.

    NOTE: 
    We need the vim Python module.
    Therefore, we must run these unit tests in VIM.
    Steps:
    1. Open "plugin/vim_fanfou.vim" in vim
    2. Run :so %
    3. call VimFanfouTests()

    :copyright: (c) 2014 by xiong-jia.le ( lexiongjia@gmail.com )
    :license: Vim license. See :help license
"""

import unittest
from . import misc_unittest

def vim_fanfou_tests():
    test_loader = unittest.TestLoader()
    suite = test_loader.loadTestsFromTestCase(misc_unittest.BaseTests)
    unittest.TextTestRunner().run(suite)

