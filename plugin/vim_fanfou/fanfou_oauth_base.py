#!/usr/bin/env python

import time, binascii, uuid, hmac, hashlib, webbrowser, ConfigParser
import urllib
from . import misc

# startup logger
from . import logger
LOG = logger.LOGGER.get_logger()

class FanfouOAuthBase(object):
    def __init__(self, cfg):
        # auth cach filename
        self.auth_cache = cfg.get("auth_cache")

    @staticmethod
    def _escape(src_str):
        return urllib.quote(src_str.encode('utf-8'), safe='~')

    @staticmethod
    def generate_timestamp():
        return FanfouOAuthBase._escape(str(int(time.time())))

    @staticmethod
    def generate_nonce():
        return FanfouOAuthBase._escape(binascii.b2a_hex(uuid.uuid4().bytes))

    @staticmethod
    def get_full_cache_filename(filename):
        return misc.resolve_usr_filename(filename)

    @classmethod
    def open_url(cls, url):
        LOG.debug("open %s", url)
        webbrowser.open_new_tab(url)

    @classmethod
    def get_input(cls, msg):
        return raw_input(msg)

    def get_pin_code(self):
        return self.get_input("Enter PIN code: ")

    def mk_oauth_url(self, base_url, request_data, auth_keys):
        # sort the query data and create the query string
        query_data = request_data.items()
        query_data.sort()
        query_str = urllib.urlencode(query_data)

        # formate the base_str
        base_str = "GET&%s&%s" % (
            self._escape(base_url),
            self._escape(query_str)
        )

        # oauth_signature = signature(base_string)
        # signature-method = SHA1;
        # signature-key = "consumer_secret&"
        if len(auth_keys) == 1:
            key = ("%s&" % "".join(auth_keys))
        else:
            key = "&".join(auth_keys)
        sig_hash = hmac.new(key, base_str, hashlib.sha1)
        sig_item = (
            "oauth_signature",
            binascii.b2a_base64(sig_hash.digest())[:-1]
        )
        query_data.append(sig_item)
        return "%s?%s" % (base_url, urllib.urlencode(query_data))

    def mk_oauth(self, method, base_url, request_data, auth_keys):
        # base_str = "HTTP Method (GET/POST)" + "&" +
        #            "url_encode(base_url)" + "&" +
        #            sorted(querysting.items()).join('&');
        #
        # NOTE:
        # It only supports "HMAC-SHA1" signature and oauth version 1.0
        request_data["oauth_signature_method"] = "HMAC-SHA1"
        request_data["oauth_version"] = "1.0"

        # auto update oauth_timestamp & oauth_nonce
        if request_data.has_key("oauth_timestamp") != True:
            request_data["oauth_timestamp"] = self.generate_timestamp()
        if request_data.has_key("oauth_nonce") != True:
            request_data["oauth_nonce"] = self.generate_nonce()

        if method == "POST":
            # TO DO: make http hdr for POST method
            raise Exception("NO IMPL")
        elif method == "GET":
            req_url = self.mk_oauth_url(base_url, request_data, auth_keys)
            LOG.debug("OAuth GET req: %s", req_url)
            return { "req_url": req_url }
        else:
            LOG.error("Invalid HTTP method %s", method)
            raise ValueError("Invalid HTTP method")

    def get_cached_acc_token(self):
        cache_filename = self.get_full_cache_filename(self.auth_cache)
        try:
            LOG.debug("load auth cache from %s", cache_filename)
            cache = ConfigParser.RawConfigParser()
            cache.read(cache_filename)
        except Exception, err:
            LOG.warn("cannot get token from %s", cache_filename)
            raise err

        if (
            cache.has_option("acc_token", "oauth_token") != True or
            cache.has_option("acc_token", "oauth_token_secret") != True
            ):
            LOG.warn("cannot get cached token")
            raise ValueError("Invalid OAuth token")

        result = {
            "oauth_token": cache.get("acc_token", "oauth_token"),
            "oauth_token_secret": cache.get("acc_token", "oauth_token_secret")
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
        cache_filename = self.get_full_cache_filename(self.auth_cache)
        LOG.debug("save auth cache to %s", cache_filename)
        with open(cache_filename, "w") as cache_file:
            cache.write(cache_file)

