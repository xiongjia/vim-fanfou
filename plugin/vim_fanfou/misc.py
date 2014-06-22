#!/usr/bin/env python
"""
    vim_fanfou.misc:
    ~~~~~~~~~~~~~~~~
    The utility functions or objects.

    :copyright: (c) 2014 by xiong-jia.le ( lexiongjia@gmail.com )
    :license: MIT, see LICENSE for more details.
"""

import os, sys, logging, ConfigParser, time, urllib2
from email import utils as emailutils

def resolve_usr_filename(filename):
    """Resolve the filename to an absolute path.

    :param filename: The input file name.
    """
    full_filename = filename
    if os.path.isabs(full_filename) == False:
        full_filename = os.path.join(os.path.expanduser("~"),
            full_filename)
    return os.path.normpath(full_filename)

# logging object
class Log(object):
    """It's a simple wrapper of python built-in logging object."""
    # logger levels map
    _LEVELS = {
        "error": logging.ERROR,
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "critical": logging.CRITICAL,
    }

    def __init__(self, opts):
        """The constructor of Log object.

        :param opts: It's a dict of Log configuration.
        """
        self._logger = logging.getLogger()
        self._logger.addHandler(logging.NullHandler())
        self._hdlr = {}
        # set options
        self.set_options(opts)

    def set_options(self, opts):
        """To update logging configuration with the parameters

        :param opts: The log configuration.
        """
        # enable/disable console logger
        if opts.get("console", False):
            self._enable_console_logger()
        else:
            self._disable_console_logger()

        # enable/disable fs logger
        log_file = opts.get("fs", None)
        if log_file:
            self._enable_fs_logger(log_file)
        else:
            self._disable_fs_logger()

        # update log level
        level = self.get_log_level(opts.get("level", "error"))
        self._logger.setLevel(level)

        # update disable/enable flag
        self.set_disable(opts.get("disable", False))

    @staticmethod
    def get_log_level(log_level):
        """Return the logging.level

        :param log_level: The description of the log level. (e.g. "info")
        """
        return Log._LEVELS.get(log_level, logging.INFO)

    def get_logger(self):
        """Return the logger instance"""
        return self._logger

    def set_disable(self, disable):
        """Disable/Enable logger output

        :param disable: True = disable log; False = Enable log
        """
        # disable/enable the logger
        self._logger.disabled = disable

    def _enable_console_logger(self):
        """Enable console (stdout) Logger handler"""
        # enable console logger
        if self._hdlr.has_key("console") != True:
            self._hdlr["console"] = logging.StreamHandler(sys.stdout)
            self._logger.addHandler(self._hdlr["console"])

    def _disable_console_logger(self):
        """Disable console (stdout) Logger handler"""
        # disable console logger
        if self._hdlr.has_key("console"):
            self._logger.removeHandler(self._hdlr["console"])
            del self._hdlr["console"]

    def _enable_fs_logger(self, filename):
        """Enable file Logger handler

        :param filename: the log file name.
        """
        # close old fs stream
        if self._hdlr.has_key("fs"):
            self._disable_fs_logger()

        # create a new fs log stream
        full_filename = resolve_usr_filename(filename)
        self._hdlr["fs"] = logging.FileHandler(full_filename)
        self._logger.addHandler(self._hdlr["fs"])

    def _disable_fs_logger(self):
        """Disable file Logger handler"""
        # disable fs logger
        if self._hdlr.has_key("fs"):
            self._logger.removeHandler(self._hdlr["fs"])
            del self._hdlr["fs"]


# logger instance
LOGGER = Log({ "level": "error", "console": False })
LOG = LOGGER.get_logger()

def load_fanfou_oauth_config(conf_filename):
    """Load fanfou oauth config from a file (This function only for test)

    :param conf_filename: configuration filename
    """
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
        LOG.warn("Cannot load oauth config from %s; err %s",
            full_filename, err)
        raise err

def chk_keys(keys, src_list):
    """Check the keys are included in the src_list

    :param keys: the keys need to check
    :param src_list: the source list
    """
    for key in keys:
        if key not in src_list:
            return False
    return True

def parse_tm_str(tm_str):
    """Parse a time string and return the local ctime string.
    The python built-in Time module cannot parse time zone info.
    Therefore, we create this function.

    :param tm_str: The source time string.
        (e.g. Fri Jun 20 14:00:03 +0000 2014)
    """
    try:
        tm_tuple = emailutils.parsedate_tz(tm_str)
        tm_val = emailutils.mktime_tz(tm_tuple)
        local_tm = time.ctime(tm_val)
    except Exception, err:
        LOG.warn("Cannot parse %s; err %s", tm_str, err)
        return tm_str
    else:
        return local_tm

def install_urllib_proxy(http_proxy):
    LOG.debug("install proxy %s", http_proxy)
    if not http_proxy:
        return
    try:
        proxy_hdlr = urllib2.ProxyHandler({ 'http': http_proxy })
        opener = urllib2.build_opener(proxy_hdlr)
        urllib2.install_opener(opener)
    except Exception, err:
        LOG.error("Cannot install proxy %s; err: %s", http_proxy, err)

def main():
    """Test function"""
    LOGGER.set_options({
        "level": "debug",
        "console": True,
        "fs": "vim-fanfou.log",
    })
    LOG.debug("misc")
    cfg = load_fanfou_oauth_config(".fanfou.cfg")
    LOG.debug("oauth config %s", cfg)

    tm_str = parse_tm_str("Fri Jun 20 14:00:03 +0000 2014")
    LOG.debug("tm %s", tm_str)

if __name__ == "__main__":
    main()

