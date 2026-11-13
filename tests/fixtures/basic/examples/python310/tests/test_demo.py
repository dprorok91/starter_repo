from pathlib import Path
import sys
import unittest

from demo import greet


class GreetingTests(unittest.TestCase):
    def test_greeting(self):
        self.assertEqual(greet(' Ada '), 'Hello, Ada!')

    def test_empty_name(self):
        with self.assertRaises(ValueError):
            greet(' ')

    def test_selected_runtime(self):
        expected = Path('.python-version').read_text().strip()
        actual = f'{sys.version_info.major}.{sys.version_info.minor}'
        self.assertEqual(actual, expected)
