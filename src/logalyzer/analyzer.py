# -*- coding:utf-8 -*-
import heapq
from operator import itemgetter

from client_request import ClientRequest
from utils import heap_percentile


class Analyzer(object):

    def __init__(self, file_obj, process=False):
        self.file_object = file_obj

        self.request_times = []
        self.open_requests = {}

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

        return heap_percentile(percentile, self.request_times, key=itemgetter(1))[1]

    def get_slowest_requests(self, number):
        """
        Get specified number of slowes requests. Returns list of tuples (request_id, duration)
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

    def start_request(self, timestamp, request_id):
        """
        Process StartRequest event
        """

        self.open_requests[request_id] = ClientRequest(request_id, timestamp)

    def finish_request(self, timestamp, request_id):
        """
        Process FinishRequest event
        """

        request = self.open_requests[request_id]
        request.finish_time = timestamp
        heapq.heappush(self.request_times, (request.id, request.duration))
        del self.open_requests[request_id]
