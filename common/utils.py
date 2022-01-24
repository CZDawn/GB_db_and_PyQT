import json
import sys

sys.path.append('../')

from common.variables import DEFAULT_ENCODING, DEFAULT_MAX_PACKAGES_LENGTH
from decorators import log_decorator


@log_decorator
def get_message(sender) -> dict:
    ''' Processes the received message.
    Returns the message in dictionary format.
     '''
    obtained_message = sender.recv(DEFAULT_MAX_PACKAGES_LENGTH)
    decoded_message = obtained_message.decode(DEFAULT_ENCODING)
    dict_format_message = json.loads(decoded_message)
    if isinstance(dict_format_message, dict):
        return dict_format_message
    raise TypeError


@log_decorator
def send_message(addressee, message) -> None:
    json_format_message_to_send = json.dumps(message)
    encoded_message = json_format_message_to_send.encode(DEFAULT_ENCODING)
    addressee.send(encoded_message)

