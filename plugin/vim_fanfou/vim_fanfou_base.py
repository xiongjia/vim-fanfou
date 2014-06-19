#!/usr/bin/env python

from . import misc

# startup logger
LOG = misc.LOGGER.get_logger()

class VimFanfouBase(object):
    DEFAULT_CFG = {
        "consumer_key": "df51b20a9dcd93e13abe1f22389f5372",
        "consumer_secret": "1a3cfd7b5b752e5521c7b26ae07b2401",
        "auth_cache": ".fanfou_auth_cache",
        "log_file": None,
        "log_level": "debug",
        "buf_name": "VimFanfou",
    }

    def __init__(self, vim_util):
        self._vim = vim_util

    @staticmethod
    def check_cfg_item(cfg, item):
        return cfg[item] if cfg[item] else VimFanfouBase.DEFAULT_CFG[item]

    @staticmethod
    def set_logger_options(opts):
        misc.LOGGER.set_options(opts)

    def update_buf_syntax(self):
        self._vim.vim_batch([
            "syntax clear",
            r"syntax match fanfouUsr /^.\{-1,}:/",
            "highlight default link fanfouUsr Identifier",
        ])

    def switch_to_buf(self, buf_name):
        bufnr = self._vim.bufwinnr("^%s$" %  buf_name)
        if bufnr > 0:
            # switch to current buff
            self._vim.vim_cmd("%dwincmd w" % bufnr)
        else:
            # create a new buf
            self._vim.vim_batch([
                "new %s" % buf_name,
                "setlocal noswapfile",
                "setlocal buftype=nofile",
                "setlocal bufhidden=delete",
                "setlocal foldcolumn=0",
                "setlocal nobuflisted",
                "setlocal nospell",
                "setlocal filetype=fanfouvim",
            ])
            self.update_buf_syntax()

        cur_buf_name = self._vim.vim_eval("bufname('%')")
        if cur_buf_name != buf_name:
            LOG.error("Cannot create/find fanfou vim buf")
            return None
        vim = self._vim.get_vim_mod()
        return vim.current.buffer

