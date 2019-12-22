"""Test nothing."""
import unittest


class TestNothing(unittest.TestCase):
    def setUp(self):
        self._nothing = True

    def test_nothing(self):
        assert self._nothing
