#!/usr/bin/env python
"""
    vim_fanfou.vim_util:
    ~~~~~~~~~~~~~~~~~~~
    VimUtil is a simple Python wrapper for VIM python module.

    :copyright: (c) 2014 by xiong-jia.le ( lexiongjia@gmail.com )
    :license: Vim license. See :help license
"""

from . import misc
LOG = misc.LOGGER.get_logger()

class VimUtil(object):
    """VimUtil is a simple Python wrapper for VIM python module."""
    def __init__(self):
        """The constructor of VimUtil"""
        self._vim = None

    def set_vim_mod(self, vim):
        """Update the VIM python module"""
        self._vim = vim

    def get_vim_mod(self):
        """Return the current VIM python module"""
        return self._vim

    def vim_eval(self, exp):
        """A wrapper for VIM.eval()"""
        return self._vim.eval(exp)

    def vim_cmd(self, cmd):
        """A wrapper for VIM.command()"""
        self._vim.command(cmd)

    def vim_batch(self, cmd_list):
        """Run a list of the VIM commands."""
        self.vim_cmd(" | ".join(cmd_list))

    def get_val(self, var_name, default_ret = ""):
        """Return a specific VIM var.
        :param var_name: the name of this specific var.
        :param default_ret: this value will be returned
            if the specific var dose not exist in VIM.
        """
        return self.vim_eval("exists('%s') ? %s : '%s'" %
            (var_name, var_name, default_ret))

    def _show_msg_level(self, level, msg):
        """Show a message in VIM command buf with the specific level
        :param level: the level description (ErrorMsg; WarningMsg; None)
        :param msg: the message string.
        """
        normal_msg = msg.replace("'", " ")
        normal_msg = normal_msg.replace("\"", " ")
        normal_msg = normal_msg.replace("\n", " ")
        self.vim_batch([
            "redraw",
            "echohl %s" % level,
            "echomsg '%s'" % normal_msg,
            "echohl None",
        ])

    def show_msg_normal(self, msg):
        """Show a normal message
        :param msg: the message string.
        """
        self._show_msg_level("None", msg)

    def show_msg_err(self, msg):
        """Show an error message
        :param msg: the message string.
        """
        self._show_msg_level("ErrorMsg", msg)

    def show_msg_warn(self, msg):
        """Show a warning message
        :param msg: the message string.
        """
        self._show_msg_level("WarningMsg", msg)

    def bufwinnr(self, name):
        """A wrapper for VIM bufwinnr command
        :param name: the name of the target buffer
        """
        try:
            bufnr = int(self.vim_eval("bufwinnr('%s')" % name))
        except Exception, err:
            LOG.warn("bufwinnr (%s) err: %s", name, err)
            return -1
        else:
            return bufnr

    def vim_input(self, prompt):
        """A wrapper of VIM input command
        :param prompt: the prompt string
        """
        self.vim_batch([
            "call inputsave()",
            "redraw"])
        ret_val = self.vim_eval("input('%s')" % prompt)
        self.vim_cmd("call inputrestore()")
        return ret_val


class VimBuffModifiable(object):
    """Set the current buffer to modifiable in the with scope
    For Example:
        with VimUtil.VimBuffModifiable(VIM):
            buf[:] = None
    """
    def __init__(self, vim_util):
        """Construct function
        :param vim_util: the VimUtil object
        """
        self._vim_util = vim_util

    def __enter__(self):
        """Set the target VIM buffer to modifiable"""
        self._vim_util.vim_cmd("setlocal modifiable")
        return self

    def __exit__(self, type, value, traceback):
        """Set the target VIM buffer to read only"""
        self._vim_util.vim_cmd("setlocal nomodifiable")


