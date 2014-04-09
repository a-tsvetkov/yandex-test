# -*- coding:utf-8 -*-
import random
import unittest
from StringIO import StringIO

from logalyzer import Analyzer, stats
from logalyzer.requests import ClientRequest

FIXTURE = """1390672572320679	0	StartRequest
1390672572331061	0	BackendConnect	1	http://backend1-001.yandex.ru:1495/search?
1390672572331534	0	BackendConnect	0	http://backend0-001.yandex.ru:1848/search?
1390672572331939	0	BackendConnect	2	http://backend2-001.yandex.ru:1789/search?
1390672572332019	0	BackendConnect	4	http://backend4-002.yandex.ru:1445/search?
1390672572332896	0	BackendConnect	3	http://backend3-002.yandex.ru:1433/search?
1390672572370445	0	BackendRequest	2
1390672572371253	0	BackendRequest	4
1390672572376201	0	BackendRequest	0
1390672572381722	0	BackendRequest	1
1390672572389323	0	BackendRequest	3
1390672572823197	0	BackendOk	2
1390672572832417	0	BackendOk	0
1390672572871253	0	BackendError	4	ParseFromStream error
1390672572881722	0	BackendError	1	Input/output error
1390672572882606	0	BackendOk	3
1390672572882729	0	BackendConnect	4	http://backend4-001.yandex.ru:1002/search?
1390672572891737	0	BackendConnect	1	http://backend1-001.yandex.ru:1495/search?
1390672572901758	0	BackendRequest	1
1390672572915564	0	BackendRequest	4
1390672573269124	0	BackendOk	1
1390672573415564	0	BackendError	4	Connection reset by peer
1390672573425081	0	StartMerge
1390672573483245	0	StartSendResult
1390672574005831	0	FinishRequest
"""


class AnalyzerTestCase(unittest.TestCase):

    def setUp(self):
        self.file_object = StringIO(FIXTURE)

    def test_init_not_process(self):
        analyzer = Analyzer(self.file_object)

        self.assertEqual(analyzer.request_times, [])

    def test_init_process(self):
        analyzer = Analyzer(self.file_object, process=True)

        self.assertEqual(analyzer.request_times, [(0, 1685152)])

    def test_extract_params(self):
        line = "1234	4	TestEvent	14	http://test.url/search?"
        analyzer = Analyzer(StringIO())

        self.assertEqual(
            analyzer.extract_params(line),
            (1234, 4, 'TestEvent', ['14', 'http://test.url/search?'])
        )

    def test_backend_stats(self):
        analyzer = Analyzer(self.file_object, process=True)

        self.assertEqual(analyzer.backend_stats.keys(), [0, 1, 2, 3, 4])
        self.assertEqual(
            analyzer.backend_stats[4].backends,
            ['backend4-001.yandex.ru:1002', 'backend4-002.yandex.ru:1445']
        )

        backend1 = analyzer.backend_stats[0].get_backend('backend0-001.yandex.ru:1848')
        self.assertEqual(backend1.request_count, 1)

        self.assertEqual(len(analyzer.backend_stats[1].backends), 1)
        backend2 = analyzer.backend_stats[1].get_backend('backend1-001.yandex.ru:1495')
        self.assertEqual(backend2.request_count, 2)
        self.assertEqual(dict(backend2.errors), {'Input/output error': 1})

        self.assertEqual(len(analyzer.backend_stats[4].backends), 2)
        backend3 = analyzer.backend_stats[4].get_backend('backend4-001.yandex.ru:1002')
        self.assertEqual(backend3.request_count, 1)
        self.assertEqual(
            dict(backend3.errors),
            {'Connection reset by peer': 1}
        )

    def test_incomplete_requests(self):
        analyzer = Analyzer(self.file_object, process=True)

        self.assertEqual(analyzer.incomplete_request_count, 1)

    def test_process(self):
        analyzer = Analyzer(self.file_object)
        self.assertEqual(analyzer.request_times, [])

        analyzer.process()
        self.assertEqual(analyzer.request_times, [(0, 1685152)])

    def test_get_request_percentile(self):
        analyzer = Analyzer(StringIO())
        analyzer.request_times = [(i, i + 100) for i in xrange(100)]
        random.shuffle(analyzer.request_times)

        self.assertEqual(analyzer.get_request_percentile(90), 190)

    def test_get_slowest_requests(self):
        analyzer = Analyzer(StringIO())
        analyzer.request_times = [(i, i + 100) for i in xrange(100)]
        random.shuffle(analyzer.request_times)

        self.assertEqual(
            analyzer.get_slowest_requests(5),
            [(99, 199), (98, 198), (97, 197), (96, 196), (95, 195)]
        )

    def test_get_slowest_requests_more_tan_have(self):
        analyzer = Analyzer(StringIO())
        analyzer.request_times = [(i, i + 100) for i in xrange(3)]
        random.shuffle(analyzer.request_times)

        self.assertEqual(
            analyzer.get_slowest_requests(5),
            [(2, 102), (1, 101), (0, 100)]
        )

    def test_process_entry_start_request(self):
        analyzer = Analyzer(StringIO())

        analyzer.process_entry(1234, 22, 'StartRequest', [])

        self.assertIn(22, analyzer.open_requests)
        self.assertEqual(analyzer.open_requests[22].id, 22)
        self.assertEqual(analyzer.open_requests[22].start_time, 1234)

    def test_process_entry_new_backend_connect(self):
        analyzer = Analyzer(StringIO())
        analyzer.process_entry(1234, 33, 'StartRequest', [])
        analyzer.process_entry(1234, 33, 'BackendConnect', [3, 'http://test.host1:1234/path/to/resource?query'])

        self.assertEqual(analyzer.backend_stats[3].backends, ['test.host1:1234'])
        self.assertEqual(len(analyzer.open_requests[33].pending_requests), 1)
        self.assertEqual(
            analyzer.open_requests[33].pending_requests[3].host,
            'test.host1:1234'
        )

    def test_process_entry_existing_backend_connect(self):
        analyzer = Analyzer(StringIO())
        rs_stat = stats.ReplicaSetStat(3)
        rs_stat.add_backend('test.host:1234')
        rs_stat.get_backend('test.host:1234').request_count = 10
        analyzer.backend_stats[3] = rs_stat

        analyzer.process_entry(1234, 33, 'StartRequest', [])
        analyzer.process_entry(1234, 33, 'BackendConnect', [3, 'http://test.host:1234/path/to/resource?query'])

        self.assertEqual(analyzer.backend_stats[3].backends, ['test.host:1234'])
        self.assertEqual(len(analyzer.open_requests[33].pending_requests), 1)
        self.assertEqual(
            analyzer.open_requests[33].pending_requests[3].host,
            'test.host:1234'
        )

    def test_process_entry_backend_error(self):
        analyzer = Analyzer(StringIO())
        analyzer.process_entry(1234, 33, 'StartRequest', [])
        analyzer.process_entry(1234, 33, 'BackendConnect', [3, 'http://test.host1:1234/path/to/resource?query'])
        analyzer.process_entry(1234, 33, 'BackendError', [3, 'TestError'])

        self.assertEqual(
            dict(analyzer.backend_stats[3].get_backend('test.host1:1234').errors),
            {'TestError': 1}
        )
        self.assertEqual(len(analyzer.open_requests[33].pending_requests), 0)
        self.assertEqual(analyzer.open_requests[33].incomplete, True)

    def test_process_entry_finish_request(self):
        analyzer = Analyzer(StringIO())
        analyzer.open_requests[33] = ClientRequest(33, 2345)

        analyzer.process_entry(2355, 33, 'FinishRequest', [])
        self.assertNotIn(33, analyzer.open_requests)
        self.assertEqual(analyzer.request_times, [(33, 10)])

    def test_backend_ok(self):
        analyzer = Analyzer(StringIO())
        analyzer.process_entry(1234, 33, 'StartRequest', [])
        analyzer.process_entry(1234, 33, 'BackendConnect', [3, 'http://test.host1:1234/path/to/resource?query'])
        analyzer.process_entry(1234, 33, 'BackendOk', [3])

        self.assertEqual(len(analyzer.open_requests[33].pending_requests), 0)
        self.assertEqual(analyzer.open_requests[33].incomplete, False)

    def test_start_merge(self):
        analyzer = Analyzer(StringIO())
        analyzer.process_entry(1234, 33, 'StartRequest', [])
        analyzer.process_entry(1234, 33, 'BackendConnect', [3, 'http://test.host1:1234/path/to/resource?query'])
        analyzer.process_entry(1234, 33, 'StartMertge', [])

        self.assertEqual(len(analyzer.open_requests[33].pending_requests), 1)
