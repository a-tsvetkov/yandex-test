# -*- coding:utf-8 -*-
import argparse
from analyzer import Analyzer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("infile")

    args = parser.parse_args()
    print 'Processing log from {0}...'.format(args.infile)
    print
    with open(args.infile, "r") as infile:
        analyzer = Analyzer(infile, process=True)

    print "95th perccentile for request time: {0}".format(analyzer.get_request_percentile(95))
    print
    print "10 longest requests ids:"
    for request_id, time in analyzer.get_slowest_requests(10):
        print "{:>15}: {:>15}".format(request_id, time)
    print
    print "Backend requests:"
    for rs_id, rs_stats in analyzer.backend_stats.iteritems():
        print "{:>10}Replica set {}:".format('', rs_id)
        for backend_stats in rs_stats.backends_dict.itervalues():
            print "{:>15}{}".format('', backend_stats.host)
            print "{:>20}Total requests: {}".format('', backend_stats.request_count)
            if backend_stats.errors:
                print "{:>25}Errors:".format('')
                for name, count in backend_stats.errors.iteritems():
                    print "{:>30}{}: {}".format('', name, count)
            print

    print "Number of incomlete requests: {0}".format(analyzer.incomplete_request_count)


if __name__ == "__main__":
    main()
