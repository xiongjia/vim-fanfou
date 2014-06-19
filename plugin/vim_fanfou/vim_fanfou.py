#!/usr/bin/env python

from . import misc
from . import fanfou_oauth as FanfouOAuth
from . import fanfou as Fanfou
from . import vim_util as VimUtil
from . import vim_fanfou_base as VimFanfouBase

# startup logger and VIM util
LOG = misc.LOGGER.get_logger()
VIM = VimUtil.VimUtil()

class VimFanfou(VimFanfouBase.VimFanfouBase):
    VIM_FANFOU = None

    def __init__(self, cfg):
        super(VimFanfou, self).__init__(VIM)
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

        # create fanfou & oauth objects
        self._fanfou_oauth = FanfouOAuth.FanfouOAuth({
            "consumer_key": self.config["consumer_key"],
            "consumer_secret": self.config["consumer_secret"],
            "auth_cache": self.config["auth_cache"],
        })
        self._fanfou = Fanfou.Fanfou(self._fanfou_oauth)
        self._fanfou.load_token()

    @staticmethod
    def init(cfg):
        VimFanfou.VIM_FANFOU = VimFanfou(cfg)
        return VimFanfou.VIM_FANFOU

    @staticmethod
    def get_instance():
        return VimFanfou.VIM_FANFOU

    def update_home_timeline(self):
        try:
            tm_ln = self._fanfou.get_home_timeline({ "count": 3 })
        except Exception, err:
            LOG.warn("cannot update home timline %s", err)
            return

        buf = self.switch_to_buf(self.config["buf_name"])
        if not buf:
            LOG.error("create switch to fanfou buf")
            return

        # update timeline to buffer
        with VimUtil.VimBuffModifiable(VIM):
            buf[:] = None
            self.append_timeline(buf, tm_ln)

    @staticmethod
    def append_timeline(vim_buf, tm_ln):
        for item in tm_ln:
            vim_buf.append("%s: %s <%s>\n" %
                (item["user_name"], item["text"], item["created_at"]))

