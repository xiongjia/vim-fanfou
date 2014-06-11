#!/usr/bin/env python

import logging, sys

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


LOGGER = Log({ "level": "error", "console": False })


# The test entry function
def main():
    LOGGER.set_options({ "level": "debug", "console": True })
    log = LOGGER.get_logger()
    log.info("Test info log")
    log.error("Test error log")
    log.debug("Test debug log")

if __name__ == "__main__":
    main()

