# -*- coding:utf-8 -*-
import unittest

from logalyzer.requests import ClientRequest


class ClientRequestTestCase(unittest.TestCase):

    def test_duration(self):
        request = ClientRequest(1, 1234)
        request.finish_time = 1244

        self.assertEqual(request.duration, 10)

    def test_duration_no_finish_time(self):
        request = ClientRequest(1, 1234)

        self.assertEqual(request.duration, None)

    def test_backend_connect(self):
        request = ClientRequest(1, 1234)
        request.backend_connect(3, 'http://test.com/path/to/host')

        self.assertEqual(request.replica_set_ids, set([3]))
        self.assertEqual(len(request.pending_requests), 1)
        self.assertEqual(request.pending_requests[3].replica_set_id, 3)
        self.assertEqual(request.pending_requests[3].url, 'http://test.com/path/to/host')

    def test_backend_error(self):
        request = ClientRequest(1, 1234)
        request.backend_connect(3, 'http://test.com/path/to/host')
        request.backend_error(3)

        self.assertEqual(len(request.pending_requests), 0)

    def test_last_request_url(self):
        request = ClientRequest(1, 1234)
        request.backend_connect(3, 'http://test.com/path/to/host')

        self.assertEqual(request.last_request_url(3), 'http://test.com/path/to/host')
