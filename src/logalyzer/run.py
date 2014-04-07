# -*- coding:utf-8 -*-
import argparse
import heapq
from operator import itemgetter


class ClientRequest(object):

    def __init__(self, id, start_time, finish_time=None):
        self.id = id
        self.start_time = start_time
        self.finish_time = finish_time

        self.replica_set_ids = set()
        self.pending_requests = []

    @property
    def duration(self):
        return self.finish_time - self.start_time

    def backend_connect(self, replica_set_id, url):
        self.replica_set_ids.add(replica_set_id)
        self.pending_requests.append(BackendRequest(replica_set_id, url))


class BackendRequest(object):

    def __init__(self, replica_id, url):
        self.replica_id = replica_id
        self.url = url


def heap_percentile(p, heap, key=None):
    (nth, p) = (heapq.nsmallest, p) if p <= 50 else (heapq.nlargest, 100 - p)
    return nth(max(1, int(len(heap) * p / 100.0 + 0.5)), heap, key=key)[-1]


parser = argparse.ArgumentParser()
parser.add_argument("infile")

request_times = []
open_requests = {}

if __name__ == "__main__":
    args = parser.parse_args()
    with open(args.infile, "r") as infile:
        for line in infile:
            params = line.strip("\n").split("\t")
            timestamp, request_id, event = params[:3]
            additional_params = params[3:] if len(params) > 3 else []

            timestamp = int(timestamp)
            request_id = int(request_id)

            if event == 'StartRequest':
                open_requests[request_id] = ClientRequest(request_id, timestamp)

            if event == 'FinishRequest':
                request = open_requests[request_id]
                request.finish_time = timestamp
                heapq.heappush(request_times, (request.id, request.duration))
                del open_requests[request_id]

    percentile = heap_percentile(95, request_times, key=itemgetter(1))[1]
    slowest_requests = heapq.nlargest(10, request_times, key=itemgetter(1))

    print "95th perccentile for request time: {0}".format(percentile)
    print "10 longest requests ids:"
    for request_id, time in slowest_requests:
        print "\t", request_id, " :", time
