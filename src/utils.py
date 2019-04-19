#  -*- coding: utf-8 -*-
#
# Unitlities including
# 1. logging

import os
import logging
from datetime import datetime


def init_logger(name):
    ''' initialize a logger '''  # todo : template logger only
    if not os.path.exists('./logs/'):
        os.makedirs('./logs')
    logger = logging.getLogger(name)

    # now = datetime.strftime(datetime.now(), '%Y%m%d_%H%M')
    formatter = logging.Formatter(
        '-%(asctime)-15s-%(name)s-%(levelname)s: %(message)s')
    handler_stream = logging.StreamHandler()
    handler_stream.setFormatter(formatter)
    handler_file = logging.FileHandler('./logs/{}.log'.format(name))
    handler_file.setFormatter(formatter)
    logger.addHandler(handler_stream)
    logger.addHandler(handler_file)
    logger.setLevel(logging.INFO)
    return logger


def func_recorder(func):
    ''' func log record decorator '''

    logger = init_logger('main')

    def wrapper(*arg, **kw):
        logger.info("Begin to execute function: %s" % func.__name__)
        res = func(*arg, **kw)
        logger.info("Finish executing function: %s" % func.__name__)
        return res
    return wrapper


def get_project_path():
    """ get project path """
    dir_abs_path = os.path.dirname(os.path.abspath(__file__))
    curr_folder = dir_abs_path.split('/')[-1]
    project_path = dir_abs_path.replace(curr_folder, '')
    return project_path
