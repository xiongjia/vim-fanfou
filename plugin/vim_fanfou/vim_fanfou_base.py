#!/usr/bin/env python

from . import misc

# startup logger
LOG = misc.LOGGER.get_logger()

class VimFanfouBase(object):
    VIM = None
    DEFAULT_CFG = {
        "consumer_key": "df51b20a9dcd93e13abe1f22389f5372",
        "consumer_secret": "1a3cfd7b5b752e5521c7b26ae07b2401",
        "auth_cache": ".fanfou_auth_cache",
        "log_file": None,
        "log_level": "debug",
        "buf_name": "VimFanfou",
    }

    def __init__(self, vim_util):
        VimFanfouBase.VIM = vim_util

    @staticmethod
    def check_cfg_item(cfg, item):
        return cfg[item] if cfg[item] else VimFanfouBase.DEFAULT_CFG[item]

    @staticmethod
    def set_logger_options(opts):
        misc.LOGGER.set_options(opts)

    @staticmethod
    def switch_to_buf(buf_name):
        bufnr = VimFanfouBase.VIM.bufwinnr("^%s$" %  buf_name)
        if bufnr > 0:
            # switch to current buff
            VimFanfouBase.VIM.vim_cmd("%dwincmd w" % bufnr)
        else:
            # create a new buf
            VimFanfouBase.VIM.vim_batch([
                "new %s" % buf_name,
                "setlocal noswapfile",
                "setlocal buftype=nofile",
                "setlocal bufhidden=delete",
                "setlocal foldcolumn=0",
                "setlocal nobuflisted",
                "setlocal nospell",
            ])
        cur_buf_name = VimFanfouBase.VIM.vim_eval("bufname('%')")
        if cur_buf_name != buf_name:
            LOG.error("Cannot create/find fanfou vim buf")
            return None
        vim = VimFanfouBase.VIM.get_vim_mod()
        return vim.current.buffer

