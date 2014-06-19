#!/usr/bin/env python

from . import misc
LOG = misc.LOGGER.get_logger()

class VimUtil(object):
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
        self.vim_cmd(" | ".join(cmd_list))

    def get_val(self, var_name, default_ret = ""):
        return self.vim_eval("exists('%s') ? %s : '%s'" %
            (var_name, var_name, default_ret))

    def _show_msg_level(self, level, msg):
        self.vim_batch([
            "redraw",
            "echohl %s" % level,
            "echomsg %s" % msg,
            "echohl None",
        ])

    def show_msg_normal(self, msg):
        self._show_msg_level("None", msg)

    def show_msg_err(self, msg):
        self._show_msg_level("ErrorMsg", msg)

    def show_msg_warn(self, msg):
        self._show_msg_level("WarningMsg", msg)

    def bufwinnr(self, name):
        try:
            bufnr = int(self.vim_eval("bufwinnr('%s')" % name))
        except Exception, err:
            LOG.warn("bufwinnr (%s) err: %s", name, err)
            return -1
        else:
            return bufnr

class VimBuffModifiable(object):
    def __init__(self, vim_util):
        self._vim_util = vim_util

    def __enter__(self):
        self._vim_util.vim_cmd("setlocal modifiable")
        return self

    def __exit__(self, type, value, traceback):
        self._vim_util.vim_cmd("setlocal nomodifiable")


