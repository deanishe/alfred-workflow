#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2015 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2015-01-24
#

"""
"""

from __future__ import print_function, unicode_literals, absolute_import

import logging
import logging.handlers

try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, *args, **kwargs):
            pass


def get_logger(name):
    """Get :class:`logging.Logger` for ``name``

    Ensures at least a :class:`logging.NullHandler` is set.

    """
    logger = logging.getLogger(name)
    # Ensure a handler is set on root to avoid warnings
    root = logging.getLogger('')
    if len(root.handlers) == 0:
        root.addHandler(NullHandler())

    return logger


def init_logging(console=True, logfile=None, level=logging.INFO):
    """Add handlers to root logger and set log level"""
    fmt_str = ('%(asctime)s %(filename)s:%(lineno)s'
               ' %(levelname)-8s %(message)s')
    logger = logging.getLogger('')
    if console:
        hdlr = logging.StreamHandler()
        fmt = logging.Formatter(fmt_str, datefmt='%H:%M:%S')
        hdlr.setFormatter(fmt)
        logger.addHandler(hdlr)
    if logfile is not None:
        hdlr = logging.handlers.RotatingFileHandler(logfile,
                                                    maxBytes=1024*1024,
                                                    backupCount=0)
        fmt = logging.Formatter(fmt_str, datefmt='%H:%M:%S')
        hdlr.setFormatter(fmt)
        logger.addHandler(hdlr)
    logger.setLevel(level)
