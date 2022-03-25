#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 17:27:12 2020

@author: Hrishikesh Terdalkar
"""

db_host = 'localhost'
db_user = 'dcs_user'
db_pass = ''
db_name = 'dcs'
db_port = 3306

###############################################################################

db_options = {
    'charset': 'utf8',
    'sql_mode': 'PIPES_AS_CONCAT',
    'use_unicode': True
}

###############################################################################

opt_str = '&'.join([f'{k}={v}' for k, v in db_options.items()])
mysql_url = (
    f'mysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}?{opt_str}'
)

###############################################################################
