import unittest

import sys
sys.path.append("./")

class Tests(unittest.TestCase):

    def test_dummy(self):
        self.assertTrue("a" == "a")
