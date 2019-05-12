#  -*- coding: utf-8 -*-
#
# Unitlities including
# 1. logging

import os
import json
import logging
import subprocess
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


def get_project_path(file_name):
    """ get project path """
    dir_abs_path = os.path.dirname(os.path.abspath(file_name))
    project_path = dir_abs_path
    return project_path


def import_conf(file_path):
    ''' read configuration json file, return as dict'''
    with open(file_path, 'r') as f:
        raw_conf = ''.join([line for line in f.readlines() if not line.strip().startswith('//')])
        json_conf = json.loads(raw_conf)
    conf = {key: [(int(idx), *[val if val else 'null' for _, val in fields.items()])
                  for idx, fields in value.items()]
            for key, value in json_conf.items()}
    return conf


def import_conf_query(file_path):
    '''read insert conf sql file, return as dict'''
    with open(file_path, 'r') as f:
        raw_sql = ''.join([line for line in f.readlines() if not line.strip().startswith('--') and line.strip()])
    splited_sql = [query for query in raw_sql.split(';') if query]
    dict_sql = [(query.split()[2], query.strip()+';') for query in splited_sql]
    return dict(dict_sql)


def del_db(file_path):
    '''drop db if fail to init'''
    subprocess.run(['rm', file_path])
    print('Drop db.')
