# -*- coding:utf-8 -*-
import unittest

from logalyzer import stats


class ReplicaSetStatTestCase(unittest.TestCase):

    def test_backends(self):
        rs_stat = stats.ReplicaSetStat(0)

        rs_stat.add_backend('test.host1')
        rs_stat.add_backend('test.host2')

        self.assertIn('test.host1', rs_stat.backends)
        self.assertIn('test.host2', rs_stat.backends)

    def test_get_backend(self):
        rs_stat = stats.ReplicaSetStat(0)

        rs_stat.add_backend('test.host1')
        rs_stat.add_backend('test.host2')

        self.assertEqual(rs_stat.get_backend('test.host1').host, 'test.host1')

    def test_get_backend_for_url(self):
        rs_stat = stats.ReplicaSetStat(0)

        rs_stat.add_backend('test.host1:1234')
        rs_stat.add_backend('test.host1:4321')

        self.assertEqual(
            rs_stat.get_backend_for_url('http://test.host1:1234/path/to/resource?query').host,
            'test.host1:1234'
        )

    def test_new_backend_connect(self):
        rs_stat = stats.ReplicaSetStat(0)
        rs_stat.backend_connect('http://test.host:1234/path/to/resource?query')

        self.assertEqual(rs_stat.backends, ['test.host:1234'])
        self.assertEqual(rs_stat.get_backend('test.host:1234').request_count, 1)

    def test_existing_backend_connect(self):
        rs_stat = stats.ReplicaSetStat(0)
        rs_stat.add_backend('test.host:1234')
        rs_stat.get_backend('test.host:1234').request_count = 10

        rs_stat.backend_connect('http://test.host:1234/path/to/resource?query')

        self.assertEqual(rs_stat.backends, ['test.host:1234'])
        self.assertEqual(rs_stat.get_backend('test.host:1234').request_count, 11)

    def test_add_backend(self):
        rs_stat = stats.ReplicaSetStat(0)
        rs_stat.add_backend('test.host:1234')

        self.assertEqual(len(rs_stat.backends), 1)
        self.assertEqual(rs_stat.backends_dict['test.host:1234'].host, 'test.host:1234')

    def test_backend_error(self):
        rs_stat = stats.ReplicaSetStat(0)
        rs_stat.add_backend('test.host:1234')

        rs_stat.backend_error('http://test.host:1234/path/to/resource?query', 'TestError')

        self.assertEqual(rs_stat.get_backend('test.host:1234').errors['TestError'], 1)
