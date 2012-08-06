from lovegov.modernpolitics.backend import *

import unittest

class ComparisonTestCase(unittest.TestCase):

    fixtures = ['test_fixture.json']

    def setUp(self):
        self.katy = getUser("Katy Perry")
        self.randy = getUser("Randy Johnson")

    def testIdentity(self):
        randomAnswers(self.katy)
        comparison = self.katy.getComparison(self.katy)
        self.assertEqual(comparison.result, 100)