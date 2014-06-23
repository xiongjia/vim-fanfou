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
    def get_input(cls, prompt):
        return VIM.vim_input(prompt)


class VimFanfou(VimFanfouBase.VimFanfouBase):
    VIM_FANFOU = None

    def __init__(self, cfg):
        super(VimFanfou, self).__init__(VIM, cfg)
        # create fanfou & oauth objects
        self._fanfou_oauth = VimFanfouOAuth(self.get_oauth_conf())
        self._fanfou = Fanfou.Fanfou(self._fanfou_oauth)
        try:
            self._fanfou.load_token()
        except Exception, err:
            LOG.warn("Cannot load oauth token; err %s", err)

    @staticmethod
    def init(cfg):
        VimFanfou.VIM_FANFOU = VimFanfou(cfg)
        return VimFanfou.VIM_FANFOU

    @staticmethod
    def get_instance():
        return VimFanfou.VIM_FANFOU

    def post_status(self, msg):
        VIM.show_msg_normal("Posting status ...")
        try:
            self._fanfou.statuses_update(msg)
        except Exception, err:
            VIM.show_msg_err("Cannot post status; err: %s" % err)
            return

        # display finish message
        VIM.show_msg_normal("Your status was sent.")

    def update_home_timeline(self):
        VIM.show_msg_normal("Updating Home Timeline ...")
        try:
            tm_ln = self._fanfou.get_home_timeline({
                "count": self.get_timeline_count(),
            })
        except Exception, err:
            LOG.warn("cannot update home timline %s", err)
            VIM.show_msg_err("Cannot update Home Timeline; err: %s" % err)
            return

        buf = self.switch_to_buf(self.config["buf_name"])
        if not buf:
            LOG.error("create switch to fanfou buf")
            VIM.show_msg_err("Cannot update Home Timeline;"
                "err: Cannot create a new buffer.")
            return

        # update timeline to buffer
        with VimUtil.VimBuffModifiable(VIM):
            buf[:] = None
            self.add_hdr(buf, "Fanfou Home Timeline")
            self.append_timeline(buf, tm_ln)

        # display finish message
        VIM.show_msg_normal("Home Timeline has updated")


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
            line_msg = line_msg.replace("\n", " ")
            try:
                vim_buf.append(line_msg)
            except Exception, err:
                LOG.warn("cannot append message to buf; err %s", err)

    def get_timeline_count(self):
        max_timeline_count = 60
        return min(max_timeline_count, self.config["fanfou_timeline_count"])

    def login(self):
        try:
            acc_token = self._fanfou_oauth.get_new_acc_token()
            self._fanfou_oauth.update_auth_cache(acc_token)
        except Exception, err:
            VIM.show_msg_err("Cannot get OAuth token; err: %s" % err)
        else:
            VIM.show_msg_normal("Fanfou OAuth Token is saved")

        try:
            self._fanfou.load_token()
        except Exception, err:
            LOG.warn("cannot load acc token; err: %s", err)

