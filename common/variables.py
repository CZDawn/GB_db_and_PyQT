from logging import INFO

# Default settings
DEFAULT_IP_ADDRESS = '127.0.0.1'
DEFAULT_PORT = 7777
DEFAULT_ENCODING = 'utf-8'
DEFAULT_MAX_QUEUE_LENGTH = 5
DEFAULT_MAX_PACKAGES_LENGTH = 1024
DEFAULT_LOGGING_LEVEL = INFO
DEFAULT_LOGGING_FORMAT = '%(asctime)s - %(levelname)-8s - %(module)s - %(message)s'
DEFAULT_SERVER_DATABASE = 'sqlite:///server_base.db3'

# JIM-protocol settings
ACTION = 'action'
USER = 'user'
TIME = 'time'
RESPONSE = 'response'
PRESENCE = 'presence'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TEXT = 'message_text'
SENDER = 'sender'
EXIT = 'exit'
RECIPIENT = 'recipient'

# Responses
RESPONSE_200 = {
    RESPONSE: 200
}
RESPONSE_300 = {
    RESPONSE: 300,
    ERROR: None
}
RESPONSE_400 = {
    RESPONSE: 400,
    ERROR:None
}

