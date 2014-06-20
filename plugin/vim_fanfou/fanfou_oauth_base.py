#!/usr/bin/env python

import time, webbrowser, ConfigParser
import binascii, uuid, hmac, hashlib
import urllib, urllib2
from . import misc

# startup logger
LOG = misc.LOGGER.get_logger()

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
    def get_input(cls, prompt):
        return raw_input(prompt)

    @staticmethod
    def get_sig_key(auth_keys):
        if len(auth_keys) == 1:
            key = ("%s&" % "".join(auth_keys))
        else:
            key = "&".join(auth_keys)
        return key

    @staticmethod
    def oauth_sig_hash(base_str, auth_keys):
        key = FanfouOAuthBase.get_sig_key(auth_keys)
        sig_hash = hmac.new(key, base_str, hashlib.sha1)
        return binascii.b2a_base64(sig_hash.digest())[:-1]

    @staticmethod
    def get_oauth_sig_item(base_str, auth_keys):
        sig_hash = FanfouOAuthBase.oauth_sig_hash(base_str, auth_keys)
        return ("oauth_signature", sig_hash)

    @staticmethod
    def get_normalized_urlstr(data):
        return urllib.urlencode(data).replace("+", "%20").replace("%7E", "~")

    @staticmethod
    def send_req(req_opts):
        if req_opts["method"] == "GET":
            LOG.debug("send GET req: %s", req_opts["uri"])
            req = urllib2.Request(req_opts["uri"])
        elif req_opts["method"] == "POST":
            LOG.debug("send POST req: %s", req_opts["uri"])
            req = urllib2.Request(req_opts["uri"],
                    data = req_opts["data"],
                    headers = req_opts["header"])
        else:
            LOG.error("Invalid method %s", req_opts["method"])
            raise ValueError("Invalid HTTP method")

        try:
            rep = urllib2.urlopen(req)
            data = rep.read()
        except urllib2.HTTPError, http_err:
            LOG.error("Cannot access target server. HTTP code %s",
                http_err.code)
            raise http_err
        except Exception, err:
            LOG.error("HTTP Request error %s", err)
            raise err
        else:
            LOG.debug("HTTP repLen=%d", len(data))
            return data

    def get_pin_code(self):
        return self.get_input("Enter the PIN code: ")

    def mk_oauth_query_data(self, opts):
        # sort the query data and create the query string
        query_data = opts["req_data"].items()
        query_data.sort()
        query_str = self.get_normalized_urlstr(query_data)

        # base_str = "HTTP Method (GET/POST)" + "&" +
        #            "url_encode(base_url)" + "&" +
        #            sorted(querysting.items()).join('&');
        base_str = "%s&%s&%s" % (opts["method"],
            self._escape(opts["base_url"]), self._escape(query_str))
        LOG.debug("base str: %s", base_str)

        # oauth_signature = signature(base_string)
        # signature-method = SHA1;
        # signature-key = "consumer_secret&access_secret"
        sig_item = self.get_oauth_sig_item(base_str, opts["auth_keys"])
        query_data.append(sig_item)
        return query_data

    def mk_oauth_hdr(self, query_data):
        oauth_params = ((key, val) for key, val in query_data
                            if key.startswith('oauth_'))
        stringy_params = ((key, self._escape(str(val)))
                            for key, val in oauth_params)
        header_params = ("%s=\"%s\"" % (key, val)
                            for key, val in stringy_params)
        params_hdr = ','.join(header_params)
        auth_hdr = "OAuth "
        if params_hdr:
            auth_hdr = "%s %s" % (auth_hdr, params_hdr)
        LOG.debug("Hdr: %s", auth_hdr)
        return { "Authorization": auth_hdr }

    def mk_oauth(self, opts):
        if opts["method"] not in ("GET", "POST"):
            LOG.error("Invalid HTTP method: %s", opts["method"])
            raise ValueError("Invalid HTTP method")

        # Fanfou only supports "HMAC-SHA1" signature and oauth version 1.0
        req_data = opts.get("req_data")
        req_data["oauth_signature_method"] = "HMAC-SHA1"
        req_data["oauth_version"] = "1.0"

        # auto update oauth_timestamp & oauth_nonce
        if req_data.has_key("oauth_timestamp") != True:
            req_data["oauth_timestamp"] = self.generate_timestamp()
        if req_data.has_key("oauth_nonce") != True:
            req_data["oauth_nonce"] = self.generate_nonce()

        # make query data
        query_data = self.mk_oauth_query_data(opts)

        if opts["method"] == "GET":
            # make GET uri
            return {
                "method": "GET",
                "uri": "%s?%s" % (opts["base_url"],
                    self.get_normalized_urlstr(query_data)),
            }
        else:
            # make POST header&body
            hdr = { "Content-Type": "application/x-www-form-urlencoded" }
            hdr.update(self.mk_oauth_hdr(query_data))
            return {
                "method": "POST",
                "uri": opts["base_url"],
                "data": self.get_normalized_urlstr(query_data),
                "header": hdr,
            }

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

    def send_oauth_req(self, opts):
        oauth_req = self.mk_oauth(opts)
        return self.send_req(oauth_req)

