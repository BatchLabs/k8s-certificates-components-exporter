#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from logging.handlers import TimedRotatingFileHandler


def get_logger():
    logger = logging.getLogger("Rotating Log")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s :: %(levelname)s :: %(message)s')

    handler = TimedRotatingFileHandler('/log/monitor.log',
                                       when="d",
                                       interval=1,
                                       backupCount=3)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)
    logger.info('Starting...')
    return logger
