#!/usr/bin/env python

from . import misc

# startup logger
LOG = misc.LOGGER.get_logger()


# The test entry function
def main():
    misc.LOGGER.set_options({ "level": "debug", "console": True })
    LOG.debug("vim fanfou")

if __name__ == "__main__":
    main()

