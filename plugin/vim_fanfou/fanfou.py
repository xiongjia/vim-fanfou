#!/usr/bin/env python

from . import fanfou_base as FanfouBase

# startup logger
from . import logger
LOG = logger.LOGGER.get_logger()

class Fanfou(FanfouBase.FanfouBase):
    def __init__(self, fanfou_oauth):
        super(Fanfou, self).__init__(fanfou_oauth)


# The test entry function
def main():
    logger.LOGGER.set_options({ "level": "debug", "console": True })
    LOG.debug("fanfou")

if __name__ == "__main__":
    main()

