#!/usr/bin/env python
"""
    vim_fanfou.vim_fanfou_base:
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    The base object for vim_fanfou

    :copyright: (c) 2014 by xiong-jia.le ( lexiongjia@gmail.com )
    :license: Vim license. See :help license
"""

import time
from . import misc
LOG = misc.LOGGER.get_logger()

class VimFanfouBase(object):
    """The base object for VimFanfou"""
    # default configurations
    DEFAULT_CFG = {
        "consumer_key": "df51b20a9dcd93e13abe1f22389f5372",
        "consumer_secret": "1a3cfd7b5b752e5521c7b26ae07b2401",
        "auth_cache": ".fanfou_auth_cache",
        "log_file": None,
        "log_level": "debug",
        "buf_name": "VimFanfou",
        "fanfou_timeline_count": 50,
        "fanfou_http_proxy": None,
    }
    VIM_OPTS = {
        "sytax_enabled": True
    }

    def __init__(self, vim_util, cfg):
        self._vim = vim_util
        # check config
        self.config = self.mk_cfg_items(cfg, [
            "consumer_key",
            "consumer_secret",
            "auth_cache",
            "buf_name",
            "fanfou_http_proxy",
            "fanfou_timeline_count",
        ])
        # update logger options
        self.set_logger_options({
            "console": False,
            "fs": self.check_cfg_item(cfg, "log_file"),
            "level": self.check_cfg_item(cfg, "log_level"),
        })
        # update vim settings
        self.update_vim_settings()
        # update http proxy
        if self.config["fanfou_http_proxy"]:
            misc.install_urllib_proxy(self.config["fanfou_http_proxy"])

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
    def mk_cfg_items(cfg, cfg_items):
        ret_cfg = {}
        for cfg_item in cfg_items:
            ret_cfg[cfg_item] = VimFanfouBase.check_cfg_item(cfg, cfg_item)
        return ret_cfg

    @staticmethod
    def check_cfg_item(cfg, item):
        if not cfg.has_key(item):
            return VimFanfouBase.DEFAULT_CFG[item]
        return cfg[item] if cfg[item] else VimFanfouBase.DEFAULT_CFG[item]

    @staticmethod
    def set_logger_options(opts):
        misc.LOGGER.set_options(opts)

    def update_buf_key_map(self):
        self._vim.vim_batch([
            "nnoremap <buffer> <silent> <Leader><Leader> :FanfouRefresh<cr>",
            "nnoremap <buffer> <silent> <Leader>h :FanfouHomeTimeline<cr>",
            "nnoremap <buffer> <silent> <Leader>m :FanfouMentions<cr>",
            "nnoremap <buffer> <silent> <Leader>s :FanfouFavorites<cr>",
            "nnoremap <buffer> <silent> <Leader>p :FanfouPostStatus<cr>",
        ])

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
            # reply
            r"syn match fanfouReply /\w\@<!@\(\w\|\.\|[^\x00-\x7f]\)\+/",
            "hi default link fanfouReply Label",
            # title
            r"syn match fanfouTitle " +
            r"/^\%(\w\+:\)\@!.\+\*$/ contains=fanfouTitleStar",
            r"syn match fanfouTitleStar /\*$/ contained",
            "hi default link fanfouTitle Title",
            "hi default link fanfouTitleStar FanfouIgnore",
            # hash
            r"syn match fanfouHash /#[^#]\+#/",
            "hi default link fanfouHash Underlined",
            # web url
            r"syn match FanfouUrl " +
            r"'\%(https\=://\|www\.\)[a-zA-Z0-9_./\-:@]\+'",
            "hi default link FanfouUrl Underlined",
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
            self.update_buf_key_map()

        cur_buf_name = self._vim.vim_eval("bufname('%')")
        if cur_buf_name != buf_name:
            LOG.error("Cannot create/find fanfou vim buf")
            return None
        vim = self._vim.get_vim_mod()
        return vim.current.buffer

    def add_hdr(self, vim_buf, title, add_tm = True):
        if add_tm:
            print_title = "%s (%s)*" % (title, time.ctime())
        else:
            print_title = "%s*" % title
        self._vim.vim_cmd("call setline('.', '%s')" % print_title)
        hdr_bar = "%s*" % ("=" * (len(print_title) + 3))
        vim_buf.append(hdr_bar)


