#!/usr/bin/env python

import urllib2, json
from . import fanfou_base as FanfouBase

# startup logger
from . import logger
LOG = logger.LOGGER.get_logger()

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
        base_url = self.urls["update"]
        data = {
            "status": status
        }
        api_req = self.mk_api_req({
            "method": "POST",
            "base_url": base_url,
            "req_data": data,
        })
        LOG.debug("postXX- %s", api_req)
        try:
            request = urllib2.Request(api_req["uri"],
                data = api_req["data"],
                headers = api_req["header"])
            rep = urllib2.urlopen(request)
            data = rep.read()
        except Exception, err:
            LOG.error("cannot update status, err %s", err)
            raise err

        # parse response
        LOG.debug("got home timeline: datalen=%d", len(data))
        try:
            results = json.loads(data)
        except Exception, err:
            LOG.error("cannot parse home_timeline json")
            raise ValueError("Invalid JSON")

        LOG.debug("rep data: %s", results)

    def get_home_timeline(self, request_args):
        base_url = self.urls["home_timeline"]
        api_req = self.mk_api_req({
            "method": "GET",
            "base_url": base_url,
            "req_data": request_args,
        })
        uri = api_req["uri"]
        LOG.debug("get home time line %s", uri)
        try:
            request = urllib2.Request(uri)
            rep = urllib2.urlopen(request)
            data = rep.read()
        except urllib2.HTTPError, http_err:
            LOG.error("Cannot access %s; HTTP code %s",
                base_url, http_err.code)
            raise http_err
        except Exception, err:
            LOG.error("cannot access home timeline, err %s", err)
            raise err

        # parse response
        LOG.debug("got home timeline: datalen=%d", len(data))
        try:
            results = json.loads(data)
        except Exception, err:
            LOG.error("cannot parse home_timeline json")
            raise ValueError("Invalid JSON")

        ret_val = []
        LOG.debug("results len=%d", len(results))
        for item in results:
            if ("id", "text", "created_at", "user") in item.keys():
                continue

            user = item["user"]
            if ("id", "name") in user.keys():
                continue

            ret_item = {
                "id": item["id"],
                "text": item["text"],
                "created_at": item["created_at"],
                "user_id": user["id"],
                "user_name": user["name"],
            }
            if item.has_key("photo"):
                ret_item["photo"] = item["photo"]
            ret_val.append(ret_item)
        return ret_val


# The test entry function
def main():
    from . import fanfou_oauth as FanfouOAuth
    from . import misc

    logger.LOGGER.set_options({ "level": "debug", "console": True })
    LOG.debug("fanfou")

    oauth_cfg = misc.load_fanfou_oaut_config(".fanfou.cfg")
    ff_oauth = FanfouOAuth.FanfouOAuth(oauth_cfg)
    fanfou = Fanfou(ff_oauth)
    fanfou.load_token()
    # Read time line
    # tm_lines = fanfou.get_home_timeline({ "count": 1 })
    # LOG.debug("Timeline: len=%d", len(tm_lines))
    # for tm_ln in tm_lines:
    #     LOG.debug("usr: %s (%s) - msg: %s",
    #         tm_ln["user_name"], tm_ln["created_at"], tm_ln["text"])
    #     if tm_ln.has_key("photo"):
    #         LOG.debug("photo: %s", tm_ln["photo"])
    #     LOG.debug("---------------------")

    # Status post 
    # fanfou.statuses_update("Fanfou OAuth Test")

if __name__ == "__main__":
    main()

