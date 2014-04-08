# -*- coding:utf-8 -*-
import unittest
import heapq
import operator

from logalyzer import utils


class UtilsTestCase(unittest.TestCase):

    def test_heap_percentile_no_key_range(self):
        heap = range(100)
        heapq.heapify(heap)

        self.assertEqual(utils.heap_percentile(95, heap), 95)

    def test_heap_percentile_with_key(self):
        heap = [{'key': value} for value in xrange(10)]
        heapq.heapify(heap)

        self.assertEqual(utils.heap_percentile(90, heap, key=operator.itemgetter('key')), {'key': 9})
