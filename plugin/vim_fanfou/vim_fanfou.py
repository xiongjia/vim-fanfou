#!/usr/bin/env python

from . import misc

# startup logger
LOG = misc.LOGGER.get_logger()

class Vim(object):
    def __init__(self):
        self._vim = None

    def set_vim_mod(self, vim):
        self._vim = vim

    def get_vim_mod(self):
        return self._vim

    def vim_eval(self, src):
        return self._vim.eval(src)

    def get_val(self, var_name, default_ret = ""):
        return self.vim_eval("exists('%s') ? %s : '%s'" %
            (var_name, var_name, default_ret))

    def get_vim_current(self):
        return self._vim.current


VIM = Vim()


class VimFanfou(object):
    VIM_FANFOU = None

    def __init__(self, cfg):
        self.config = {
            "consumer_key": cfg.get("consumer_key"),
            "consumer_secret": cfg.get("consumer_secret"),
            "auth_cache": cfg.get("auth_cache", ".fanfou_auth_cache"),
            "buff_name": cfg.get("buff_name", "_fanfou_buf_"),
        }
        buf = VIM.get_vim_current().buffer
        buf.append("CFG: %s" % self.config)

    @staticmethod
    def init(cfg):
        VimFanfou.VIM_FANFOU = VimFanfou(cfg)
        return VimFanfou.VIM_FANFOU

    @staticmethod
    def set_logger_options(opts):
        pass


