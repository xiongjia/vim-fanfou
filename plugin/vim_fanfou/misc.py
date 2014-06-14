#!/usr/bin/env python

import os, ConfigParser

# startup logger
from . import logger
LOG = logger.LOGGER.get_logger()

def resolve_usr_filename(filename):
    full_filename = filename
    if os.path.isabs(full_filename) == False:
        full_filename = os.path.join(os.path.expanduser("~"),
            full_filename)
    return os.path.normpath(full_filename)

def load_fanfou_oaut_config(conf_filename):
    full_filename = resolve_usr_filename(conf_filename)

    LOG.debug("Load oauth config from %s", full_filename)
    try:
        cfg = ConfigParser.RawConfigParser()
        cfg.read(full_filename)
        return {
            "consumer_key": cfg.get("fanfou", "consumer_key"),
            "consumer_secret": cfg.get("fanfou", "consumer_secret"),
            "auth_cache": cfg.get("fanfou", "auth_cache"),
        }
    except Exception, err:
        LOG.warn("Cannot load config from %s; err %s",
            full_filename, err)
        raise err

# The test entry function
def main():
    logger.LOGGER.set_options({ "level": "debug", "console": True })
    LOG.debug("misc")
    cfg = load_fanfou_oaut_config(".fanfou.cfg")
    LOG.debug("oauth config %s", cfg)

if __name__ == "__main__":
    main()

