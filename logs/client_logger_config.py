import os
import sys
from logging import getLogger, Formatter, StreamHandler, ERROR, FileHandler

sys.path.append(os.path.join(os.getcwd(), '..'))

from common.variables import DEFAULT_ENCODING, DEFAULT_LOGGING_LEVEL, \
                             DEFAULT_LOGGING_FORMAT

try:
    os.mkdir(f'{os.path.join(os.path.dirname(__file__))}/log_files')
    PATH = os.path.join(os.path.dirname(__file__), 'log_files/client.log')
except OSError:
    PATH = os.path.join(os.path.dirname(__file__), 'log_files/client.log')

LOG = getLogger('client_logger')

CLIENT_FORMATTER = Formatter(DEFAULT_LOGGING_FORMAT)

ERROR_HANDLER = StreamHandler(sys.stderr)
ERROR_HANDLER.setFormatter(CLIENT_FORMATTER)
ERROR_HANDLER.setLevel(ERROR)

LOG_FILE = FileHandler(PATH, encoding=DEFAULT_ENCODING)
LOG_FILE.setFormatter(CLIENT_FORMATTER)
LOG.setLevel(DEFAULT_LOGGING_LEVEL)

LOG.addHandler(ERROR_HANDLER)
LOG.addHandler(LOG_FILE)


if __name__ == '__main__':
    LOG.info('INFO')
    LOG.debug('DEBUG')
    LOG.warning('WARNING')
    LOG.error('ERROR')
    LOG.critical('CRITICAL')

