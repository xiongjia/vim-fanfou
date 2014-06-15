#!/usr/bin/env python

from . import misc

# startup logger
LOG = misc.LOGGER.get_logger()

class VimFanfou(object):
    def __init__(self, cfg):
        self.config = {
            "consumer_key": cfg.get("consumer_key"),
            "consumer_secret": cfg.get("consumer_secret"),
            "auth_cache": cfg.get("auth_cache", ".fanfou_auth_cache"),
        }

    @staticmethod
    def set_logger_options(opts):
        pass

