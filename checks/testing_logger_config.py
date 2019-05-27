#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from logging.handlers import TimedRotatingFileHandler


def get_logger():
    logger = logging.getLogger("Rotating Log")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s :: %(levelname)s :: %(message)s')

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)

    return logger
