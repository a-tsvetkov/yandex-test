# -*- coding:utf-8 -*-
import heapq
from operator import itemgetter

from requests import ClientRequest
from stats import ReplicaSetStat
import utils


class Analyzer(object):

    def __init__(self, file_obj, process=False):
        self.file_object = file_obj

        self.request_times = []
        self.open_requests = {}

        self.backend_stats = {}
        self.incomplete_request_count = 0

        if process:
            self.process()

    def process(self):
        """
        Process the log file line by line
        """

        for line in self.file_object:
            self.process_entry(*self.extract_params(line))

    def get_request_percentile(self, percentile):
        """
        Returns specified percentile of request duratgion in processed log
        """

        return utils.heap_percentile(percentile, self.request_times, key=itemgetter(1))[1]

    def get_slowest_requests(self, number):
        """
        Get specified number of slowest requests. Returns list of tuples (request_id, duration)
        """

        return heapq.nlargest(number, self.request_times, key=itemgetter(1))

    def extract_params(self, raw_line):
        """
        Extract data from tab separated log line
        """

        params = raw_line.strip("\n").split("\t")
        timestamp, request_id, event = params[:3]
        additional_params = params[3:] if len(params) > 3 else []

        timestamp = int(timestamp)
        request_id = int(request_id)

        return timestamp, request_id, event, additional_params

    def process_entry(self, timestamp, request_id, event, additional_params):
        """
        Process event for log entry
        """

        if event == 'StartRequest':
            self.start_request(timestamp, request_id)

        if event == 'FinishRequest':
            self.finish_request(timestamp, request_id)

        if event == 'BackendConnect':
            replica_set_id, request_url = additional_params
            replica_set_id = int(replica_set_id)
            self.backend_connect(timestamp, request_id, replica_set_id, request_url)

        if event == 'BackendError':
            replica_set_id, error_code = additional_params
            replica_set_id = int(replica_set_id)

            self.backend_error(timestamp, request_id, replica_set_id, error_code)

        if event == 'BackendOk':
            replica_set_id = additional_params[0]
            replica_set_id = int(replica_set_id)

            self.backend_ok(timestamp, request_id, replica_set_id)

        if event == 'StartMerge':
            self.start_merge(timestamp, request_id)

    def start_request(self, timestamp, request_id):
        """
        Process StartRequest event
        """

        self.open_requests[request_id] = ClientRequest(request_id, timestamp)

    def backend_connect(self, timestamp, request_id, replica_set_id, request_url):
        """
        Process BackendConnect event

        Extract host here for optimisation puropose
        """

        host = utils.get_host(request_url)
        self.open_requests[request_id].backend_connect(replica_set_id, host)

        if replica_set_id not in self.backend_stats:
            self.backend_stats[replica_set_id] = ReplicaSetStat(replica_set_id)
        self.backend_stats[replica_set_id].backend_connect(host)

    def backend_error(self, timestamp, request_id, replica_set_id, error):
        """
        Process BackendError event
        """

        request = self.open_requests[request_id]
        backend_host = request.last_request_host(replica_set_id)

        request.backend_error(replica_set_id)
        self.backend_stats[replica_set_id].backend_error(backend_host, error)

    def backend_ok(self, timestamp, request_id, replica_set_id):
        self.open_requests[request_id].backend_ok(replica_set_id)

    def start_merge(self, timestamp, request_id):
        if self.open_requests[request_id].incomplete:
            self.incomplete_request_count += 1

    def finish_request(self, timestamp, request_id):
        """
        Process FinishRequest event
        """

        request = self.open_requests[request_id]
        request.finish_time = timestamp
        heapq.heappush(self.request_times, (request.id, request.duration))
        del self.open_requests[request_id]
