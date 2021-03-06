#!/usr/bin/env python
"""
    vim_fanfou.fanfou:
    ~~~~~~~~~~~~~~~~~~
    Fanfou is the wrapper for Fanfou API.

    :copyright: (c) 2014 by xiong-jia.le ( lexiongjia@gmail.com )
    :license: Vim license. See :help license
"""


from . import fanfou_base as FanfouBase
from . import misc
LOG = misc.LOGGER.get_logger()

class Fanfou(FanfouBase.FanfouBase):
    def __init__(self, fanfou_oauth):
        super(Fanfou, self).__init__(fanfou_oauth)
        # api URLs
        self.urls = {
            "home_timeline":
                "http://api.fanfou.com/statuses/home_timeline.json",
            "update":
                "http://api.fanfou.com/statuses/update.json",
            "mentions":
                "http://api.fanfou.com/statuses/mentions.json",
            "favorites":
                "http://api.fanfou.com/favorites/id.json",
        }

    def statuses_update(self, status):
        # check status length
        status_len = misc.mbstrlen(status)
        if status_len > 140:
            raise Exception("Invalid status; Too many characters. " +
                            "It was not sent.")
        elif status_len <= 0:
            raise Exception("Invalid status; It is an empty string." +
                " It was not sent.")

        # send status
        data = { "status": status }
        try:
            rep_data = self.send_api_req({
                "method": "POST",
                "base_url": self.urls["update"],
                "req_data": data,
            })
        except Exception, err:
            LOG.error("cannot update status, err %s", err)
            raise err

        # parse post message result
        return self.parse_rep_message(rep_data)

    def get_home_timeline(self, opts):
        data = {
            "count": opts.get("count", 10),
        }
        try:
            rep_data = self.send_api_req({
                "method": "GET",
                "base_url": self.urls["home_timeline"],
                "req_data": data,
            })
        except Exception, err:
            LOG.error("cannot access home timeline, err %s", err)
            raise err
        # parse response
        return self.parse_rep_messages(rep_data)

    def get_statuses_mentions(self, opts):
        data = {
            "count": opts.get("count", 10),
        }
        try:
            rep_data = self.send_api_req({
                "method": "GET",
                "base_url": self.urls["mentions"],
                "req_data": data,
            })
        except Exception, err:
            LOG.error("cannot access status mentions, err %s", err)
            raise err
        # parse response
        return self.parse_rep_messages(rep_data)

    def get_favorites(self, opts):
        data = {
            "count": opts.get("count", 10),
        }
        try:
            rep_data = self.send_api_req({
                "method": "GET",
                "base_url": self.urls["favorites"],
                "req_data": data,
            })
        except Exception, err:
            LOG.error("cannot access favorites, err %s", err)
            raise err
        return self.parse_rep_messages(rep_data)


# The test entry function
def main():
    from . import fanfou_oauth as FanfouOAuth

    misc.LOGGER.set_options({ "level": "debug", "console": True })
    LOG.debug("fanfou")

    oauth_cfg = misc.load_fanfou_oauth_config(".fanfou.cfg")
    ff_oauth = FanfouOAuth.FanfouOAuth(oauth_cfg)
    fanfou = Fanfou(ff_oauth)
    fanfou.load_token()
    # > Read time line
    # tm_lines = fanfou.get_home_timeline({ "count": 1 })
    # LOG.debug("Timeline: len=%d", len(tm_lines))
    # for tm_ln in tm_lines:
    #     LOG.debug("usr: %s (%s) - msg: %s",
    #         tm_ln["user_name"], tm_ln["created_at"], tm_ln["text"])
    #     LOG.debug("---------------------")
    # > statuses mentions
    # mentions = fanfou.get_statuses_mentions({ "count": 10 })
    # LOG.debug("mentions: len=%d", len(mentions))
    # for mention in mentions:
    #     LOG.debug("usr: %s (%s) - msg: %s",
    #         mention["user_name"], mention["created_at"], mention["text"])
    #     LOG.debug("---------------------")
    # > favorites
    # favorites = fanfou.get_favorites({ "count": 10 })
    # LOG.debug("favorites: len=%d", len(favorites))
    # for fav in favorites:
    #     LOG.debug("usr: %s (%s) - msg: %s",
    #         fav["user_name"], fav["created_at"], fav["text"])
    #     LOG.debug("---------------------")
    # > Status post
    # ret_item = fanfou.statuses_update("Fanfou API Test")
    # LOG.debug("post %s", ret_item)

if __name__ == "__main__":
    main()

