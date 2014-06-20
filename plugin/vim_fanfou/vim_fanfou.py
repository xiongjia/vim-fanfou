#!/usr/bin/env python

from . import misc
from . import fanfou_oauth as FanfouOAuth
from . import fanfou as Fanfou
from . import vim_util as VimUtil
from . import vim_fanfou_base as VimFanfouBase

# startup logger and VIM util
LOG = misc.LOGGER.get_logger()
VIM = VimUtil.VimUtil()

class VimFanfouOAuth(FanfouOAuth.FanfouOAuth):
    def __init__(self, cfg):
        super(VimFanfouOAuth, self).__init__(cfg)

    @classmethod
    def get_instance(cls, prompt):
        return VIM.vim_input(prompt)


class VimFanfou(VimFanfouBase.VimFanfouBase):
    VIM_FANFOU = None

    def __init__(self, cfg):
        super(VimFanfou, self).__init__(VIM, cfg)
        # create fanfou & oauth objects
        self._fanfou_oauth = VimFanfouOAuth(self.get_oauth_conf())
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

    def append_timeline(self, vim_buf, tm_ln):
        self.add_hdr(vim_buf, "Fanfou Home Timeline")
        for item in tm_ln:
            vim_buf.append("%s: %s |%s|" % (
                item["user_name"],
                item["text"],
                misc.parse_tm_str(item["created_at"]),
            ))

    @staticmethod
    def add_hdr(vim_buf, title):
        VIM.vim_cmd("call setline('.', '%s')" % title)
        vim_buf.append("======================")

