import os
import logging

logging.basicConfig(level=logging.INFO)


__version__ = '1.0.1'

TOKEN = os.environ.get('TOKEN', '')

MYSQL_CONFIG = {
    'MYSQL_HOST': os.environ.get('MYSQL_HOST', 'localhost'),
    'MYSQL_PORT': int(os.environ.get('MYSQL_PORT', 1234)),
    'MYSQL_USER': os.environ.get('MYSQL_USER', 'guest'),
    'MYSQL_PASSWORD': os.environ.get('MYSQL_PASSWORD', ''),
    'MYSQL_DATABASE': os.environ.get('MYSQL_DATABASE', 'foo'),
    'MYSQL_ROOT_PASSWORD': os.environ.get('MYSQL_ROOT_PASSWORD', '')
}