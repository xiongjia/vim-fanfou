#!/usr/bin/env python
"""
    vim_fanfou.vim_fanfou:
    ~~~~~~~~~~~~~~~~~~~
    It is the interfaces for vim_fanfou.vim

    :copyright: (c) 2014 by xiong-jia.le ( lexiongjia@gmail.com )
    :license: Vim license. See :help license
"""

from . import misc
from . import fanfou_oauth as FanfouOAuth
from . import fanfou as Fanfou
from . import vim_util as VimUtil
from . import vim_fanfou_base as VimFanfouBase
from . import fanfou_data as FanfouData

LOG = misc.LOGGER.get_logger()
VIM = VimUtil.VimUtil()

class VimFanfouOAuth(FanfouOAuth.FanfouOAuth):
    """Just to rewrite the get_input() method in FanfouOAuth object"""
    def __init__(self, cfg):
        """Construct function"""
        super(VimFanfouOAuth, self).__init__(cfg)

    @classmethod
    def get_input(cls, prompt):
        """Call vim_input() for get the PIN code"""
        return VIM.vim_input(prompt)


class VimFanfou(VimFanfouBase.VimFanfouBase):
    """All the Fanfou API interfaces"""
    # The instance of VimFanfou object
    VIM_FANFOU = None

    def __init__(self, cfg):
        """constructor function
        :param cfg: all config data
        """
        super(VimFanfou, self).__init__(VIM, cfg)
        # create fanfou & oauth objects
        self._fanfou_oauth = VimFanfouOAuth(self.get_oauth_conf())
        self._fanfou = Fanfou.Fanfou(self._fanfou_oauth)
        try:
            self._fanfou.load_token()
        except Exception, err:
            LOG.warn("Cannot load oauth token; err %s", err)

        # current data
        self._cur_dat = FanfouData.FanfouData()

    @staticmethod
    def init(cfg):
        """Create an new VimFanfou object and save the instance to VIM_FANFOU
        :param cfg: all the config data
        """
        VimFanfou.VIM_FANFOU = VimFanfou(cfg)
        return VimFanfou.VIM_FANFOU

    @staticmethod
    def get_instance():
        """Get the saved instance"""
        return VimFanfou.VIM_FANFOU

    def post_status(self, msg):
        """Post a status to Fanfou
        :param msg: the post message string
        """
        VIM.show_msg_normal("Posting status ...")
        try:
            post_item = self._fanfou.statuses_update(msg)
        except Exception, err:
            VIM.show_msg_err("Cannot post status; err: %s" % err)
            return

        data_type = FanfouData.FanfouDataType.HOME_TIMELINE
        self._cur_dat.push_item(data_type, post_item)
        self._show_cur_data()

        # display finish message
        VIM.show_msg_normal("Your status was sent.")

    def update_favorites(self):
        """Get the Fanfou favorites and update it VIM buffer"""
        VIM.show_msg_normal("Updating favorites...")
        try:
            favorites = self._fanfou.get_favorites({
                "count": self.get_timeline_count(),
            })
        except Exception, err:
            LOG.warn("cannot favorites %s", err)
            VIM.show_msg_err("Cannot update favorites; err: %s" % err)
            return

        data_type = FanfouData.FanfouDataType.FAVORITES
        self._cur_dat.set_items(data_type, favorites)
        if not self._show_cur_data():
            VIM.show_msg_err("Cannot update favorites; "
                "err: Cannot update vim buffer.")
        else:
            # display finish message
            VIM.show_msg_normal("Favorites timeline has been updated")


    def update_mentions(self):
        """Get the Fanfou home time line and update it VIM buffer"""
        VIM.show_msg_normal("Updating mentions...")
        try:
            tm_ln = self._fanfou.get_statuses_mentions({
                "count": self.get_timeline_count(),
            })
        except Exception, err:
            LOG.warn("cannot update mentions %s", err)
            VIM.show_msg_err("Cannot update mentions; err: %s" % err)
            return

        data_type = FanfouData.FanfouDataType.MENTIONS
        self._cur_dat.set_items(data_type, tm_ln)
        if not self._show_cur_data():
            VIM.show_msg_err("Cannot update mentions; "
                "err: Cannot update vim buffer.")
        else:
            # display finish message
            VIM.show_msg_normal("Mentions timeline has been updated")

    def update_home_timeline(self):
        """Get the Fanfou home time line and update it VIM buffer"""
        VIM.show_msg_normal("Updating Home Timeline ...")
        try:
            tm_ln = self._fanfou.get_home_timeline({
                "count": self.get_timeline_count(),
            })
        except Exception, err:
            LOG.warn("cannot update home timline %s", err)
            VIM.show_msg_err("Cannot update Home Timeline; err: %s" % err)
            return

        data_type = FanfouData.FanfouDataType.HOME_TIMELINE
        self._cur_dat.set_items(data_type, tm_ln)
        if not self._show_cur_data():
            VIM.show_msg_err("Cannot update Home Timeline; "
                "err: Cannot update vim buffer.")
        else:
            # display finish message
            VIM.show_msg_normal("Home Timeline has been updated")

    def _show_cur_data(self):
        """Update the self._cur_dat to the VIM buffer
        :param title: The title string will be add to
            the first line of the buffer
        """
        buf = self.switch_to_buf(self.config["buf_name"])
        if not buf:
            LOG.error("Cannot create/switch to fanfou buf")
            return False

        # update timeline to buffer
        title = self._cur_dat.get_data_title()
        with VimUtil.VimBuffModifiable(VIM):
            buf[:] = None
            self.add_hdr(buf, title)
            self.append_timeline(buf, self._cur_dat.get_items())
        return True

    def refresh(self):
        """refresh the Fanfou buffer"""
        data_type = self._cur_dat.get_data_type()
        if data_type == FanfouData.FanfouDataType.MENTIONS:
            self.update_mentions()
        elif data_type == FanfouData.FanfouDataType.FAVORITES:
            self.update_favorites()
        else:
            self.update_home_timeline()

    @classmethod
    def append_timeline(cls, vim_buf, tm_ln):
        """Append time line data to VIM buffer
        :param vim_buf: the Python VIM buffer object.
        :param tm_ln: the time line data
        """
        for item in tm_ln:
            if item.has_key("photo_url"):
                line_msg = "%s: %s %s |%s|" % (
                    item["user_name"].encode("utf8"),
                    misc.MSG_CONV.FromHTMLStr(item["text"]),
                    item["photo_url"].encode("utf8"),
                    misc.parse_tm_str(item["created_at"]))
            else:
                line_msg = "%s: %s |%s|" % (
                    item["user_name"].encode("utf8"),
                    misc.MSG_CONV.FromHTMLStr(item["text"]),
                    misc.parse_tm_str(item["created_at"]))

            # add to vim buf
            line_msg = line_msg.replace("\n", " ")
            try:
                vim_buf.append(line_msg)
            except Exception, err:
                LOG.warn("Cannot append message to buf; err %s", err)

    def get_timeline_count(self):
        """Return the count of the time line count
        (In this version, the count must in [0, 60])
        """
        max_timeline_count = 60
        count = min(max_timeline_count, self.config["fanfou_timeline_count"])
        if count <= 0:
            count = max_timeline_count
        return count

    def login(self):
        """Switch to a new Fanfou account - Create and save a new
            Fanfou OAuth Token
        """
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
            LOG.warn("Cannot load OAuth Token; err: %s", err)

