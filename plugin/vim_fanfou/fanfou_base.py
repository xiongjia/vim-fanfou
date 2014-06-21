#!/usr/bin/env python

import json
from . import misc

# startup logger
LOG = misc.LOGGER.get_logger()

class FanfouBase(object):
    def __init__(self, fanfou_oauth):
        self.oauth = fanfou_oauth
        self.acc_token = {}
        self.acc_token_loaded = False

    def load_token(self, auto_renew = False):
        try:
            self.acc_token = self.oauth.get_cached_acc_token()
            self.acc_token_loaded = True
            LOG.debug("loaded cached acc token")
        except Exception, err:
            LOG.debug("cannot load cached acc token")
            if auto_renew != True:
                LOG.debug("cannot get cached acc token")
                raise err
            # create a new acc token
            LOG.debug("requesting a new acc token")
            self.acc_token = self.oauth.get_new_acc_token()
            LOG.debug("updating acc token cache, %s", self.acc_token)
            self.oauth.update_auth_cache(self.acc_token)
            self.acc_token_loaded = True

    def mk_api_req(self, opts):
        if self.acc_token_loaded != True:
            LOG.error("Invalid Access Token")
            raise ValueError("Invalid Access Token")

        consumer_secret = self.oauth.oauth_config["consumer_secret"]
        consumer_key = self.oauth.oauth_config["consumer_key"]
        acc_token_secret = self.acc_token["oauth_token_secret"]

        opts["req_data"].update({
            "oauth_consumer_key": consumer_key,
            "oauth_token": self.acc_token["oauth_token"],
        })
        opts["auth_keys"] = [consumer_secret, acc_token_secret]
        return self.oauth.mk_oauth(opts)

    def send_api_req(self, opts):
        api_req = self.mk_api_req(opts)
        return self.oauth.send_req(api_req)

    def parse_rep_messages(self, data):
        LOG.debug("parse rep, dataLen = %d", len(data))
        try:
            results = json.loads(data)
        except Exception, err:
            LOG.error("Invalid JSON object")
            raise err

        ret_val = []
        LOG.debug("parse msg, len=%d", len(results))
        msg_keys = ("id", "text", "created_at", "user")
        usr_keys = ("id", "name")
        for item in results:
            if misc.chk_keys(msg_keys, item.keys()) != True:
                continue

            usr = item["user"]
            if misc.chk_keys(usr_keys, usr.keys()) != True:
                continue

            ret_item = {
                "id": item["id"],
                "text": item["text"],
                "created_at": item["created_at"],
                "user_id": usr["id"],
                "user_name": usr["name"],
            }

            if item.has_key("photo"):
                ret_item.update(self.parse_photo(item["photo"]))

            ret_val.append(ret_item)

        return ret_val

    @staticmethod
    def parse_photo(photo_data):
        if not photo_data:
            return {}
        elif photo_data["largeurl"]:
            return { "photo_url": photo_data["largeurl"] }
        elif photo_data["imageurl"]:
            return { "photo_url": photo_data["imageurl"] }
        elif photo_data["thumburl"]:
            return { "photo_url": photo_data["thumburl"] }
        else:
            return {}


