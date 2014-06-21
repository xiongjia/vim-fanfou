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
    VIM_OPTS = {
        "sytax_enabled": True
    }

    def __init__(self, vim_util, cfg):
        self._vim = vim_util
        # check config
        self.config = {
            "consumer_key": self.check_cfg_item(cfg, "consumer_key"),
            "consumer_secret": self.check_cfg_item(cfg, "consumer_secret"),
            "auth_cache": self.check_cfg_item(cfg, "auth_cache"),
            "buf_name": self.check_cfg_item(cfg, "buf_name"),
        }
        # update logger options
        self.set_logger_options({
            "console": False,
            "fs": self.check_cfg_item(cfg, "log_file"),
            "level": self.check_cfg_item(cfg, "log_level"),
        })
        # update vim settings
        self.update_vim_settings()

    def update_vim_settings(self):
        if self._vim.vim_eval("has('syntax') && exists('g:syntax_on')"):
            self.VIM_OPTS["sytax_enabled"] = True
        else:
            self.VIM_OPTS["sytax_enabled"] = False

    def get_oauth_conf(self):
        return {
            "consumer_key": self.config["consumer_key"],
            "consumer_secret": self.config["consumer_secret"],
            "auth_cache": self.config["auth_cache"],
        }

    @staticmethod
    def check_cfg_item(cfg, item):
        return cfg[item] if cfg[item] else VimFanfouBase.DEFAULT_CFG[item]

    @staticmethod
    def set_logger_options(opts):
        misc.LOGGER.set_options(opts)

    def update_buf_syntax(self):
        if not self.VIM_OPTS["sytax_enabled"]:
            return

        self._vim.vim_batch([
            "syntax clear",
            # fanfou ignore schema
            "hi FanfouIgnore guifg=bg ctermfg=0",
            # username
            r"syn match fanfouUsr /^.\{-1,}:/",
            "hi default link fanfouUsr Identifier",
            # time stamp
            "hi FanfouTimeBar guifg=bg ctermfg=0",
            r"syn match fanfouTime /|[^|]\+|$/ contains=fanfouTimeBar",
            r"syn match fanfouTimeBar /|/ contained",
            "hi default link fanfouTimeBar FanfouIgnore",
            "hi default link fanfouTime String",
            # title
            r"syn match fanfouTitle " +
            r"/^\%(\w\+:\)\@!.\+\*$/ contains=fanfouTitleStar",
            r"syn match fanfouTitleStar /\*$/ contained",
            "hi default link fanfouTitle Title",
            "hi default link fanfouTitleStar FanfouIgnore",
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

