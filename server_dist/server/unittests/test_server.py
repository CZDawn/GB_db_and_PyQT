import os
import sys
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))

from common.variables import ACTION, PRESENCE, TIME, USER, RESPONSE, ERROR
from server import processing_message


class TestServer(unittest.TestCase):
    correct_response = {RESPONSE: 200}
    error_response  = {RESPONSE: 400, ERROR: 'Bad request'}

    def test_processing_message(self):
        answer = {ACTION: PRESENCE, TIME: 1.1, USER: 'Guest'}
        self.assertEqual(processing_message(answer), self.correct_response)

    def test_processing_message_action(self):
        answer = {ACTION: 'Hello', TIME: 1.1, USER: 'Guest'}
        self.assertEqual(processing_message(answer), self.error_response)

    def test_processing_message_no_action(self):
        answer = {TIME: 1.1, USER: 'Guest'}
        self.assertEqual(processing_message(answer), self.error_response)

    def test_processing_message_no_time(self):
        answer = {ACTION: PRESENCE, USER: 'Guest'}
        self.assertEqual(processing_message(answer), self.error_response)

    def test_processing_message_bad_user(self):
        answer = {ACTION: PRESENCE, TIME: 1.1, USER: 'Man'}
        self.assertEqual(processing_message(answer), self.error_response)

    def test_processing_message_not_user(self):
        answer = {ACTION: PRESENCE, TIME: 1.1}
        self.assertEqual(processing_message(answer), self.error_response)


if __name__ == '__main__':
    unittest.main()

