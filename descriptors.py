from logging import getLogger
from logs import server_logger_config


LOG = getLogger('server_logger')


class Port:
    def __set__(self, instance, value):
        if not 1023 < value < 65536:
            LOG.critical(
                f'Incorrect enttered port "{value}".'
            )
            sys.exit(1)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name

