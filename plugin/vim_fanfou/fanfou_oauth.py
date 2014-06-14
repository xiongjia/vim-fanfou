#!/usr/bin/env python

import urllib2, urlparse

from . import fanfou_oauth_base as FanfouOAuthBase
from . import logger
LOG = logger.LOGGER.get_logger()

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
        oauth_req = self.mk_oauth("GET", self.urls["unauth_request_token"],
            data, [self.oauth_config["consumer_secret"]])
        req_url = oauth_req["req_url"]
        LOG.debug("get unauth url %s", req_url)
        try:
            request = urllib2.Request(req_url)
            rep = urllib2.urlopen(request)
            data = rep.read()
        except urllib2.HTTPError, http_err:
            LOG.error("Cannot access %s; HTTP code %s",
                self.urls["unauth_request_token"], http_err.code)
            raise http_err
        except Exception, err:
            LOG.error("cannot get oauth req token: url = %s, err %s",
                req_url, err)
            raise err

        LOG.debug("get req token: data=%s", data)
        token = urlparse.parse_qs(data)
        if ("oauth_token", "oauth_token_secret") in token.keys():
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
            self.urls["url_authorize"], oauth_token))
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
        data = {
            "oauth_consumer_key": self.oauth_config["consumer_key"],
            "oauth_token": autho_token.get("oauth_token", ""),
            "oauth_verifier": autho_token.get("oauth_verifier", ""),
        }
        oauth_req = self.mk_oauth("GET", self.urls["acc_token"],
            data, [self.oauth_config["consumer_secret"]])
        req_url = oauth_req["req_url"]
        LOG.debug("get acc token url = %s", req_url)
        try:
            request = urllib2.Request(req_url)
            rep = urllib2.urlopen(request)
            data = rep.read()
        except urllib2.HTTPError, http_err:
            LOG.error("Cannot access %s; HTTP code %s",
                self.urls["acc_token"], http_err.code)
            raise http_err
        except Exception, err:
            LOG.error("cannot get oauth acc token: url = %s, err %s",
                req_url, err)
            raise err

        LOG.debug("get acc token: data=%s", data)
        token = urlparse.parse_qs(data)
        if ("oauth_token", "oauth_token_secret") in token.keys():
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
    from . import misc

    logger.LOGGER.set_options({ "level": "debug", "console": True })
    LOG.debug("fanfou oauth")

    oauth_cfg = misc.load_fanfou_oaut_config(".fanfou.cfg")
    ff_oauth = FanfouOAuth(oauth_cfg)
    acc_token = ff_oauth.get_cached_acc_token()
    LOG.debug("acc token %s", acc_token)

if __name__ == "__main__":
    main()

