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
            tm_ln = self._fanfou.get_home_timeline({
                "count": self.get_timeline_count(),
            })
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
            self.add_hdr(buf, "Fanfou Home Timeline")
            self.append_timeline(buf, tm_ln)

    def refresh(self):
        self.update_home_timeline()

    @classmethod
    def append_timeline(cls, vim_buf, tm_ln):
        for item in tm_ln:
            if item.has_key("photo_url"):
                line_msg = "%s: %s %s |%s|" % (
                    item["user_name"],
                    item["text"],
                    item["photo_url"],
                    misc.parse_tm_str(item["created_at"]))
            else:
                line_msg = "%s: %s |%s|" % (
                    item["user_name"],
                    item["text"],
                    misc.parse_tm_str(item["created_at"]))

            # add to vim buf
            vim_buf.append(line_msg)

    def get_timeline_count(self):
        max_timeline_count = 60
        return min(max_timeline_count, self.config["fanfou_timeline_count"])


