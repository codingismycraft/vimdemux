"""Used to test the utils.py"""

import unittest

def add(i, j):
    return i + j

class TestUtils(unittest.TestCase):
    def test_add(self):
        print("wtf11")
        self.assertEqual(2, add(1,1))

    def test_junk(self):
        breakpoint()
        print("wtf")
        self.assertEqual(2, add(1,1))
