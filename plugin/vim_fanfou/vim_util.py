#!/usr/bin/env python

from . import misc
LOG = misc.LOGGER.get_logger()

class Vim(object):
    def __init__(self):
        self._vim = None

    def set_vim_mod(self, vim):
        self._vim = vim

    def get_vim_mod(self):
        return self._vim

    def vim_eval(self, exp):
        return self._vim.eval(exp)

    def vim_cmd(self, cmd):
        self._vim.command(cmd)

    def vim_batch(self, cmd_list):
        for cmd in cmd_list:
            self.vim_cmd(cmd)

    def get_val(self, var_name, default_ret = ""):
        return self.vim_eval("exists('%s') ? %s : '%s'" %
            (var_name, var_name, default_ret))

    def show_msg(self, msg):
        self.vim_cmd("echohl None | echo '%s' | echohl None" % msg)

    def show_msg_err(self, msg):
        self.vim_cmd("echohl ErrorMsg | echo '%s' | echohl None" % msg)

    def show_msg_warn(self, msg):
        self.vim_cmd("echohl WarningMsg | echo '%s' | echohl None" % msg)

    def bufwinnr(self, name):
        try:
            bufnr = int(self.vim_eval("bufwinnr('%s')" % name))
        except Exception, err:
            LOG.warn("bufwinnr (%s) err: %s", name, err)
            return -1
        return bufnr

