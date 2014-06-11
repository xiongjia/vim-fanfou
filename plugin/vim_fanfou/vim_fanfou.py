#!/usr/bin/env python

import logger

LOG = logger.LOGGER.get_logger()

# The test entry function
def main():
    logger.LOGGER.set_options({ "level": "debug", "console": True })
    LOG.debug("vim fanfou")

if __name__ == "__main__":
    main()

