#!/usr/bin/env python

from . import logger
LOG = logger.LOGGER.get_logger()

class FanfouOAuth(object):
    def __init__(self, cfg):
        self.urls = {
            "url_unauth_request_token": "http://fanfou.com/oauth/request_token",
            "url_authorize": "http://fanfou.com/oauth/authorize",
            "url_acc_token": "http://fanfou.com/oauth/access_token",
        }
        self.oauth_config = {
           "consumer_key": cfg.get("consumer_key", ""),
           "consumer_secret": cfg.get("consumer_secret", "")
        }
        self.auth_cache = cfg.get("auth_cache")

    def get_oauth_config(self, key):
        return self.oauth_config[key]

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
        request_url = self.get_oauth_url(self.urls["url_unauth_request_token"],
            data, [self.oauth_config["consumer_secret"]])
        LOG.debug("get unauth url %s", request_url)
        request = urllib2.Request(request_url)
        try:
            rep = urllib2.urlopen(request)
            data = rep.read()
        except Exception, err:
            LOG.error("cannot get oauth req token: url = %s, err %s",
                request_url, err)
            raise err
        else:
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

        # Open the authorize page and waitting the PIN code
        self.open_url(auth_url)
        pin = self.get_pin_code()
        LOG.debug("get pin code: %s", pin)
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
        request_url = self.get_oauth_url(self.urls["url_acc_token"],
            data, [self.oauth_config["consumer_secret"]])
        LOG.debug("get acc token url = %s", request_url)
        request = urllib2.Request(request_url)
        try:
            rep = urllib2.urlopen(request)
            data = rep.read()
        except Exception, err:
            LOG.error("cannot get oauth acc token: url = %s, err %s",
                request_url, err)
            raise err
        else:
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

    def get_cached_acc_token(self):
        cache_filename = self.get_auth_cache_filename()
        try:
            LOG.debug("load auth cache from %s", cache_filename)
            cache = ConfigParser.RawConfigParser()
            cache.read(cache_filename)
        except Exception, err:
            LOG.warn("cannot get token from %s", cache_filename)
            raise err
        else:
            if (
                cache.has_option("acc_token", "oauth_token") != True or
                cache.has_option("acc_token", "oauth_token_secret") != True
            ):
                LOG.warn("cannot get cached token")
                raise ValueError("Invalid OAuth token")

            oauth_token = cache.get("acc_token", "oauth_token")
            oauth_token_secret = cache.get("acc_token", "oauth_token_secret")
            result = {
                "oauth_token": oauth_token,
                "oauth_token_secret": oauth_token_secret,
            }
            LOG.debug("get cached acc token: %s", result)
            return result

    def update_auth_cache(self, acc_token):
        cache = ConfigParser.ConfigParser()
        cache.add_section("acc_token")
        cache.set("acc_token", "oauth_token",
            acc_token.get("oauth_token"))
        cache.set("acc_token", "oauth_token_secret",
            acc_token.get("oauth_token_secret"))
        # save the toke to local cache
        cache_filename = self.get_auth_cache_filename()
        LOG.debug("save auth cache to %s", cache_filename)
        with open(cache_filename, "w") as cache_file:
            cache.write(cache_file)

    def get_auth_cache_filename(self):
        if os.path.isabs(self.auth_cache):
            filename = self.auth_cache
        else:
            filename = os.path.join(os.path.expanduser("~"), self.auth_cache)
        return os.path.normpath(filename)

    @classmethod
    def open_url(cls, url):
        LOG.debug("open %s", url)
        webbrowser.open_new_tab(url)

    @classmethod
    def get_input(cls, msg):
        return raw_input(msg)

    def get_pin_code(self):
        return self.get_input("Enter PIN code: ")

    @staticmethod
    def generate_timestamp():
        return FanfouOAuth._escape(str(int(time.time())))

    @staticmethod
    def generate_nonce():
        return FanfouOAuth._escape(binascii.b2a_hex(uuid.uuid4().bytes))

    @staticmethod
    def _escape(src_str):
        return urllib.quote(src_str.encode('utf-8'), safe='~')

    @staticmethod
    def get_oauth_url(base_url, request_data, auth_keys):
        # base_str = "HTTP Method (GET/POST)" + "&" +
        #            "url_encode(base_url)" + "&" +
        #            sorted(querysting.items()).join('&');
        #
        # NOTE:
        # 1. Currently, it only supports HTTP GET Method.
        # 2. It only supports "HMAC-SHA1" signature and 1.0 oauth version
        request_data["oauth_signature_method"] = "HMAC-SHA1"
        request_data["oauth_version"] = "1.0"

        # update oauth_timestamp & oauth_nonce if caller don't define it
        if request_data.has_key("oauth_timestamp") != True:
            request_data["oauth_timestamp"] = FanfouOAuth.generate_timestamp()
        if request_data.has_key("oauth_nonce") != True:
            request_data["oauth_nonce"] = FanfouOAuth.generate_nonce()

        # sort the query data and create the query string
        query_data = request_data.items()
        query_data.sort()
        query_str = urllib.urlencode(query_data)

        # formate the base_str
        base_str = "GET&%s&%s" % (
            FanfouOAuth._escape(base_url),
            FanfouOAuth._escape(query_str)
        )
        # oauth_signature = signature(base_string)
        # signature-method = SHA1;
        # signature-key = "consumer_secret&"
        if len(auth_keys) == 1:
            key = ("%s&" % "".join(auth_keys))
        else:
            key = "&".join(auth_keys)
        sig_hash = hmac.new(key, base_str, hashlib.sha1)
        query_data.append(
            ("oauth_signature", binascii.b2a_base64(sig_hash.digest())[:-1])
        )
        ret_url = ("%s?%s" % (base_url, urllib.urlencode(query_data)))
        LOG.debug("OAuth url %s", ret_url)
        return ret_url


# The test entry function
def main():
    logger.LOGGER.set_options({ "level": "debug", "console": True })
    LOG.debug("fanfou oauth")



if __name__ == "__main__":
    main()

