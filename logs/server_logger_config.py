import os
import sys
from logging import getLogger, Formatter, StreamHandler, ERROR, handlers

sys.path.append(os.path.join(os.getcwd(), '..'))

from common.variables import DEFAULT_ENCODING, DEFAULT_LOGGING_LEVEL, \
                                   DEFAULT_LOGGING_FORMAT

try:
    os.mkdir(f'{os.path.join(os.path.dirname(__file__))}/log_files')
    PATH = os.path.join(os.path.dirname(__file__), 'log_files/server.log')
except OSError:
    PATH = os.path.join(os.path.dirname(__file__), 'log_files/server.log')


LOG = getLogger('server_logger')

SERVER_FORMATTER = Formatter(DEFAULT_LOGGING_FORMAT)

ERROR_HANDLER = StreamHandler(sys.stderr)
ERROR_HANDLER.setFormatter(SERVER_FORMATTER)
ERROR_HANDLER.setLevel(ERROR)
LOG_FILE = handlers.TimedRotatingFileHandler(
    PATH,
    encoding=DEFAULT_ENCODING,
    interval=1,
    when='D'
)

LOG_FILE.setFormatter(SERVER_FORMATTER)
LOG.setLevel(DEFAULT_LOGGING_LEVEL)

LOG.addHandler(ERROR_HANDLER)
LOG.addHandler(LOG_FILE)


if __name__ == '__main__':
    LOG.info('INFO')
    LOG.debug('DEBUG')
    LOG.warning('WARNING')
    LOG.error('ERROR')
    LOG.critical('CRITICAL')

