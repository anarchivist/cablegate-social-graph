#!/usr/bin/env python

import unittest

import fromto


class ParseTest(unittest.TestCase):

    def test_hops(self):
        hops = fromto.hops('test-data/sample.html')
        self.assertEqual(hops, [
            (u'Venezuela', u'South America'), 
            (u'Germany', u'Europe'),
            (u'Netherlands Antilles', u'West Indies'),
            (u'Mexico', u'North America'),
            (u'Italy', u'Europe'),
            (u'Mexico', u'North America'),
            (u'Slovakia', u'Europe'),
            (u'France', u'Europe'),
            (u'United States', 'North America')])


if __name__ == "__main__":
    unittest.main()
