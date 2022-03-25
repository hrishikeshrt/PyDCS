#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 17:27:12 2020

@author: Hrishikesh Terdalkar
"""

DB_HOST = 'localhost'
DB_USER = 'dcs_user'
DB_PASS = ''
DB_NAME = 'dcs'
DB_PORT = 3306

###############################################################################

DB_OPTIONS = {
    'charset': 'utf8',
    'sql_mode': 'PIPES_AS_CONCAT',
    'use_unicode': True
}

###############################################################################

OPT_STR = '&'.join([f'{k}={v}' for k, v in DB_OPTIONS.items()])
DB_URL = (
    f'mysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?{OPT_STR}'
)

###############################################################################
