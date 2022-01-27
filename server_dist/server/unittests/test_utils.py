import os
import sys
import json
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))

from common.variables import DEFAULT_ENCODING, RESPONSE, ERROR, ACTION, \
                             PRESENCE, TIME, USER
from common.utils import send_message, get_message


class TestSocket:
    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.message_to_send = None

    def send(self, message):
        test_json_message = json.dumps(self.test_dict)
        self.encoded_message = test_json_message.encode(DEFAULT_ENCODING)
        self.message_to_send = message

    def recv(self, max_packages_length):
        json_test_message = json.dumps(self.test_dict)
        return json_test_message.encode(DEFAULT_ENCODING)


class TestUtils(unittest.TestCase):
    test_dict_to_send = {ACTION: PRESENCE, TIME: 1.1, USER: 'Guest'}
    correct_response = {RESPONSE: 200}
    error_response = {RESPONSE: 400, ERROR: 'Bad request'}

    def test_send_message(self):
        test_socket = TestSocket(self.test_dict_to_send)
        send_message(test_socket, self.test_dict_to_send)
        self.assertEqual(
            test_socket.encoded_message,
            test_socket.message_to_send
        )

    def test_get_message(self):
        test_correct_responsee = TestSocket(self.correct_response)
        test_error_response = TestSocket(self.error_response)
        self.assertEqual(
            get_message(test_correct_response),
            self.correct_response
        )
        self.assertEqual(
            get_message(test_error_response),
            self.error_response
        )
        self.assertRaises(AttributeError, get_message, 'not_dict')


if __name__ == '__main__':
    unittest.main()

