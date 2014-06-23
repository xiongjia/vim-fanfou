#!/usr/bin/env python

import urlparse

from . import fanfou_oauth_base as FanfouOAuthBase
from . import misc

# startup logger
LOG = misc.LOGGER.get_logger()

class FanfouOAuth(FanfouOAuthBase.FanfouOAuthBase):
    def __init__(self, cfg):
        super(FanfouOAuth, self).__init__(cfg)
        # Fanfou authorize URLs
        self.urls = {
            "unauth_req_token": "http://fanfou.com/oauth/request_token",
            "authorize": "http://fanfou.com/oauth/authorize",
            "acc_token": "http://fanfou.com/oauth/access_token",
        }

        # OAuth config
        self.oauth_config = {
           "consumer_key": cfg.get("consumer_key", ""),
           "consumer_secret": cfg.get("consumer_secret", ""),
        }

    def get_unauth_request_token(self):
        # get unauth request_token
        # 1. send the signed GET request to
        #    "http://fanfou.com/oauth/request_token"
        # 2. parse the response and get the unauth token
        #    For example:
        #    rep =
        #       "oauth_token=12345&oauth_token_secret=7890"
        data = {
            "oauth_consumer_key": self.oauth_config["consumer_key"],
        }
        try:
            rep_data = self.send_oauth_req({
                "method": "GET",
                "base_url": self.urls["unauth_req_token"],
                "req_data": data,
                "auth_keys": [self.oauth_config["consumer_secret"]],
            })
        except Exception, err:
            LOG.error("cannot get oauth req token: err %s", err)
            raise err

        token = urlparse.parse_qs(rep_data)
        require_keys = ("oauth_token", "oauth_token_secret")
        if misc.chk_keys(require_keys, token.keys()) != True:
            LOG.error("Invalid OAuth Token, repKeys = %s", token.keys())
            raise ValueError("Invalid OAuth token")

        result = {
            "oauth_token": "".join(token["oauth_token"]),
            "oauth_token_secret": "".join(token["oauth_token_secret"])
        }
        LOG.debug("oauth_token: %s", result)
        return result

    def get_auth_request_token(self, unauth_token):
        oauth_token = unauth_token.get("oauth_token", "")
        oauth_token_secret = unauth_token.get("oauth_token_secret", "")
        LOG.debug("token %s (%s)", oauth_token, oauth_token_secret)

        auth_url = ("%s?oauth_token=%s&oauth_callback=oob" % (
            self.urls["authorize"], oauth_token))
        LOG.debug(auth_url)

        # Open the authorize page and waitting the "PIN" code
        self.open_url(auth_url)
        pin = self.get_pin_code()
        LOG.debug("got pin code: %s", pin)
        return {
            "oauth_token": oauth_token,
            "oauth_verifier": pin,
        }

    def get_acc_token(self, autho_token):
        # send request to self.urls["acc_token"]
        data = {
            "oauth_consumer_key": self.oauth_config["consumer_key"],
            "oauth_token": autho_token.get("oauth_token", ""),
            "oauth_verifier": autho_token.get("oauth_verifier", ""),
        }
        try:
            rep_data = self.send_oauth_req({
                "method": "GET",
                "base_url": self.urls["acc_token"],
                "req_data": data,
                "auth_keys": [self.oauth_config["consumer_secret"]],
            })
        except Exception, err:
            LOG.error("cannot get oauth acc token: err %s", err)
            raise err

        # parse&verify the response token
        token = urlparse.parse_qs(rep_data)
        require_keys = ("oauth_token", "oauth_token_secret")
        if misc.chk_keys(require_keys, token.keys()) != True:
            LOG.error("Invalid OAuth Token, repKeys = %s", token.keys())
            raise ValueError("Invalid OAuth token")

        result = {
            "oauth_token": "".join(token["oauth_token"]),
            "oauth_token_secret": "".join(token["oauth_token_secret"])
        }
        LOG.debug("acc_token: %s", result)
        return result

    def get_new_acc_token(self):
        unauth_token = self.get_unauth_request_token()
        LOG.debug("get unauthon token %s", unauth_token)

        autho_token = self.get_auth_request_token(unauth_token)
        LOG.debug("get autho token: %s", autho_token)

        acc_token = self.get_acc_token(autho_token)
        LOG.debug("get acc token: %s", acc_token)
        return acc_token


# The test entry function
def main():
    misc.LOGGER.set_options({ "level": "debug", "console": True })
    LOG.debug("fanfou oauth")
    # oauth_cfg = misc.load_fanfou_oauth_config(".fanfou.cfg")
    # ff_oauth = FanfouOAuth(oauth_cfg)
    # acc_token = ff_oauth.get_new_acc_token()
    # LOG.debug("acc token %s", acc_token)
    # nonce = ff_oauth.generate_nonce()
    # LOG.debug("nonce %s", nonce)

if __name__ == "__main__":
    main()

