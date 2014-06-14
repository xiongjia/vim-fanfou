#!/usr/bin/env python

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

