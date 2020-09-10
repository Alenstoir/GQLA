import os
from dotenv import load_dotenv

try:
    with open('VERSION', 'r') as v_file:
        VERSION = v_file.readline()
except FileNotFoundError or FileExistsError:
    VERSION = 'UNDEFINED'

LOG_LEVEL_PROJECT = os.getenv('LOG_LEVEL_PROJECT', 'DEBUG')
LOG_FORMAT_PROJECT = os.getenv('LOG_FORMAT_PROJECT', '%(levelname)-8s# %(filename)s[LINE:%(lineno)d] [%(asctime)s.%(msecs)d]:  %(message)s')


LOGGING_BASE_CONFIG = {
    'version': 1,
    'formatters': {
        'default': {
            'format': LOG_FORMAT_PROJECT
        }
    },
    'handlers': {
        'console': {
            'level': LOG_LEVEL_PROJECT,
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'stream': 'ext://sys.stdout'
        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'stream': 'ext://sys.stderr'
        },
    },
    'loggings': {
        'default': {
            'level': 'DEBUG',
            'handlers': ['console', 'error']
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console', 'error']
    },
    'disable_existing_loggers': False
}
