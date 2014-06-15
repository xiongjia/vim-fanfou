#!/usr/bin/env python

import os, sys, logging, ConfigParser

# logging object
class Log(object):
    _LEVELS = {
        "error": logging.ERROR,
        "debug": logging.DEBUG,
        "info": logging.INFO
    }

    def __init__(self, opts):
        self._logger = logging.getLogger()
        self.set_options(opts)

    def set_options(self, opts):
        if opts.get("console", False):
            # enable console logger
            out_hdlr = logging.StreamHandler(sys.stdout)
            self._logger.addHandler(out_hdlr)
        # update log level
        level = self.get_log_level(opts.get("level", "info"))
        self._logger.setLevel(level)

    def get_log_level(self, log_level):
        return self._LEVELS.get(log_level, logging.INFO)

    def get_logger(self):
        return self._logger


# logger instance
LOGGER = Log({ "level": "error", "console": False })
LOG = LOGGER.get_logger()

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

def chk_keys(keys, src_list):
    for key in keys:
        if key not in src_list:
            return False
    return True

# The test entry function
def main():
    LOGGER.set_options({ "level": "debug", "console": True })
    LOG.debug("misc")
    cfg = load_fanfou_oaut_config(".fanfou.cfg")
    LOG.debug("oauth config %s", cfg)

if __name__ == "__main__":
    main()

