#!/usr/bin/env python

from . import misc
from . import fanfou_oauth as FanfouOAuth
from . import fanfou as Fanfou

# startup logger
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

    def get_val(self, var_name, default_ret = ""):
        return self.vim_eval("exists('%s') ? %s : '%s'" %
            (var_name, var_name, default_ret))

    def show_err_msg(self, msg):
        self.vim_cmd("echohl ErrorMsg | echo '%s' | echohl None" % msg)

    def show_warn_msg(self, msg):
        self.vim_cmd("echohl WarningMsg | echo '%s' | echohl None" % msg)


VIM = Vim()


class VimFanfou(object):
    VIM_FANFOU = None
    DEFAULT_CFG = {
        "consumer_key": "df51b20a9dcd93e13abe1f22389f5372",
        "consumer_secret": "1a3cfd7b5b752e5521c7b26ae07b2401",
        "auth_cache": ".fanfou_auth_cache",
        "log_file": None,
        "log_level": "debug",
    }

    def __init__(self, cfg):
        # check config
        self.config = {
            "consumer_key": self._check_cfg_item(cfg, "consumer_key"),
            "consumer_secret": self._check_cfg_item(cfg, "consumer_secret"),
            "auth_cache": self._check_cfg_item(cfg, "auth_cache"),
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

        vim = VIM.get_vim_mod()
        buf = vim.current.buffer
        for line in data:
            buf.append("usr: %s (%s) - msg: %s\n" %
                (line["user_name"], line["created_at"], line["text"]))

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

