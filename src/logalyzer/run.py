# -*- coding:utf-8 -*-
import argparse
from analyzer import Analyzer

parser = argparse.ArgumentParser()
parser.add_argument("infile")

request_times = []
open_requests = {}

if __name__ == "__main__":
    args = parser.parse_args()
    with open(args.infile, "r") as infile:
        analyzer = Analyzer(infile, process=True)

    print "95th perccentile for request time: {0}".format(analyzer.get_request_percentile(95))
    print "10 longest requests ids:"
    for request_id, time in analyzer.get_slowest_requests(10):
        print "\t", request_id, " :", time
    print "Backend requests:"
    for rs_id, rs_stats in analyzer.backend_stats.iteritems():
        print "Replica set {0}:".format(rs_id)
        for backend_stats in rs_stats.backends_dict.itervalues():
            print "\t", backend_stats.host
            print "\t\tTotal requests:", backend_stats.request_count
            if backend_stats.errors:
                print "\t\tErrors:"
                for name, count in backend_stats.errors.iteritems():
                    print "\t\t\t{0}: {1}".format(name, count)
