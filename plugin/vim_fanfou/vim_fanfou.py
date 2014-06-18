#!/usr/bin/env python

from . import misc
from . import fanfou_oauth as FanfouOAuth
from . import fanfou as Fanfou
from . import vim_util as VimUtil
from . import vim_fanfou_base as VimFanfouBase

# startup logger and VIM util
LOG = misc.LOGGER.get_logger()
VIM = VimUtil.Vim()

class VimFanfou(VimFanfouBase.VimFanfouBase):
    VIM_FANFOU = None
    DEFAULT_CFG = {
        "consumer_key": "df51b20a9dcd93e13abe1f22389f5372",
        "consumer_secret": "1a3cfd7b5b752e5521c7b26ae07b2401",
        "auth_cache": ".fanfou_auth_cache",
        "log_file": None,
        "log_level": "debug",
        "buf_name": "VimFanfou",
    }

    def __init__(self, cfg):
        super(VimFanfou, self).__init__()
        # check config
        self.config = {
            "consumer_key": self._check_cfg_item(cfg, "consumer_key"),
            "consumer_secret": self._check_cfg_item(cfg, "consumer_secret"),
            "auth_cache": self._check_cfg_item(cfg, "auth_cache"),
            "buf_name": self._check_cfg_item(cfg, "buf_name"),
        }

        # update logger options
        self.set_logger_options({
            "console": False,
            "fs": self._check_cfg_item(cfg, "log_file"),
            "level": self._check_cfg_item(cfg, "log_level"),
        })

        # create fanfou & oauth objects
        self._fanfou_oauth = FanfouOAuth.FanfouOAuth({
            "consumer_key": self.config["consumer_key"],
            "consumer_secret": self.config["consumer_secret"],
            "auth_cache": self.config["auth_cache"],
        })
        self._fanfou = Fanfou.Fanfou(self._fanfou_oauth)
        self._fanfou.load_token()

    def update_home_timeline(self):
        try:
            data = self._fanfou.get_home_timeline({ "count": 3 })
        except Exception, err:
            LOG.warn("cannot update home timline %s", err)
            return

        buf = self._switch_to_fanfou_buf()
        if not buf:
            LOG.error("create switch to fanfou buf")
            return

        for line in data:
            buf.append("usr: %s (%s) - msg: %s\n" %
                (line["user_name"], line["created_at"], line["text"]))

    def _switch_to_fanfou_buf(self):
        buf_name = self.config["buf_name"]
        bufnr = VIM.bufwinnr("^%s$" %  buf_name)
        if bufnr > 0:
            # switch to current buff
            VIM.vim_cmd("%dwincmd w" % bufnr)
        else:
            # create a new buf
            VIM.vim_batch([
                "new %s" % buf_name,
                "setlocal noswapfile",
                "setlocal buftype=nofile",
                "setlocal bufhidden=delete",
                "setlocal foldcolumn=0",
                "setlocal nobuflisted",
                "setlocal nospell",
            ])
        cur_buf_name = VIM.vim_eval("bufname('%')")
        if cur_buf_name != buf_name:
            LOG.error("Cannot create/find fanfou vim buf")
            return None
        vim = VIM.get_vim_mod()
        return vim.current.buffer

    @staticmethod
    def init(cfg):
        VimFanfou.VIM_FANFOU = VimFanfou(cfg)
        return VimFanfou.VIM_FANFOU

    @staticmethod
    def get_instance():
        return VimFanfou.VIM_FANFOU

    @staticmethod
    def _check_cfg_item(cfg, item):
        return cfg[item] if cfg[item] else VimFanfou.DEFAULT_CFG[item]

    @staticmethod
    def set_logger_options(opts):
        misc.LOGGER.set_options(opts)

