import os
import sys
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))

from client import confirm_presence, receive_message
from common.variables import TIME, ACTION, PRESENCE, USER, RESPONSE, ERROR


class TestClient(unittest.TestCase):
    """Testing module client.py"""

    def test_confirm_presence(self):
        test_message = confirm_presence()
        test_message[TIME] = 1.1
        self.assertEqual(
            test_message,
            {ACTION: PRESENCE, TIME: 1.1, USER: 'Guest'}
        )

    def test_receive_message_200(self):
        self.assertEqual(
            receive_message(
                {RESPONSE: 200}
            ),
            'Response 200: OK'
        )

    def test_receive_message_400(self):
        self.assertEqual(
            receive_message(
                {RESPONSE: 400, ERROR: 'Bad request'}
            ),
            'Response 400: Bad request'
        )

    def test_receive_message_error(self):
        self.assertEqual(
            receive_message(
                {RESPONSE: 444, ERROR: 'Bad request'}
            ),
            'Server error'
        )

    def test_receive_message_value(self):
        self.assertRaises(ValueError, receive_message, {ERROR: 'Bad request'})


if __name__ == '__main__':
    unittest.main()

