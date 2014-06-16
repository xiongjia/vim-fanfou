#!/usr/bin/env python

import vim
from . import misc

# startup logger
LOG = misc.LOGGER.get_logger()

class VimFanfou(object):
    def __init__(self, cfg):
        self.config = {
            "consumer_key": cfg.get("consumer_key"),
            "consumer_secret": cfg.get("consumer_secret"),
            "auth_cache": cfg.get("auth_cache", ".fanfou_auth_cache"),
            "buff_name": cfg.get("buff_name", "_fanfou_buf_"),
        }
        buf = vim.current.buffer
        buf.append("CFG: %s" % self.config)


    @staticmethod
    def set_logger_options(opts):
        pass


# vim fanfou instance
VIM_FANFOU = None

def vim_fanfou_init(cfg):
    VIM_FANFOU = VimFanfou(cfg)


