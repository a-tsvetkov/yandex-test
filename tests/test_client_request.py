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
        request.backend_connect(3, 'test.com')

        self.assertEqual(request.started_replica_sets, set([3]))
        self.assertEqual(len(request.pending_requests), 1)
        self.assertEqual(request.pending_requests[3].replica_set_id, 3)
        self.assertEqual(request.pending_requests[3].host, 'test.com')
        self.assertEqual(request.started_replica_sets, set([3]))

    def test_backend_finish_request(self):
        request = ClientRequest(1, 1234)
        request.backend_connect(3, 'test.com')
        request.finish_request(3)

        self.assertEqual(len(request.pending_requests), 0)

    def test_backend_ok(self):
        request = ClientRequest(1, 1234)
        request.backend_connect(3, 'test.com')
        request.backend_ok(3)

        self.assertEqual(len(request.pending_requests), 0)
        self.assertEqual(request.completed_replica_sets, set([3]))

    def test_backend_error(self):
        request = ClientRequest(1, 1234)
        request.backend_connect(3, 'test.com')
        request.backend_error(3)

        self.assertEqual(len(request.pending_requests), 0)
        self.assertEqual(request.started_replica_sets, set([3]))
        self.assertEqual(request.completed_replica_sets, set())

    def test_last_request_host(self):
        request = ClientRequest(1, 1234)
        request.backend_connect(3, 'test.com')

        self.assertEqual(request.last_request_host(3), 'test.com')

    def test_incomplete_pending(self):
        request = ClientRequest(1, 1234)
        request.backend_connect(3, 'test.com')

        self.assertEqual(request.incomplete, True)

    def test_incomplete_errors(self):
        request = ClientRequest(1, 1234)
        request.backend_connect(3, 'test.com')
        request.backend_error(3)

        self.assertEqual(request.incomplete, True)

    def test_incomplete_false(self):
        request = ClientRequest(1, 1234)
        request.backend_connect(3, 'test.com')
        request.backend_ok(3)

        self.assertEqual(request.incomplete, False)
