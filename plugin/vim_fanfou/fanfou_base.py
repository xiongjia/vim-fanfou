#!/usr/bin/env python

# startup logger
from . import logger
LOG = logger.LOGGER.get_logger()

class FanfouBase(object):
    def __init__(self, fanfou_oauth):
        self.oauth = fanfou_oauth

