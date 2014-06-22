#!/usr/bin/env python

from . import fanfou_base as FanfouBase
from . import misc

# startup logger
LOG = misc.LOGGER.get_logger()

class Fanfou(FanfouBase.FanfouBase):
    def __init__(self, fanfou_oauth):
        super(Fanfou, self).__init__(fanfou_oauth)
        # api URLs
        self.urls = {
            "home_timeline":
                "http://api.fanfou.com/statuses/home_timeline.json",
            "update":
                "http://api.fanfou.com/statuses/update.json"
        }

    def statuses_update(self, status):
        # check status length
        status_len = len(status)
        if status_len > 140:
            raise Exception("Invalid status; Too many characters. " +
                            "It was not sent.")
        elif status_len < 0:
            raise Exception("Invalid status; It's empty. It was not sent.")

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
    # > Status post
    # ret_item = fanfou.statuses_update("Fanfou API Test")
    # LOG.debug("post %s", ret_item)

if __name__ == "__main__":
    main()

