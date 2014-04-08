# -*- coding:utf-8 -*-

from backend_request import BackendRequest


class ClientRequest(object):

    def __init__(self, id, start_time, finish_time=None):
        self.id = id
        self.start_time = start_time
        self.finish_time = finish_time

        self.replica_set_ids = set()
        self.pending_requests = []

    @property
    def duration(self):
        """
        Request duration
        """

        return self.finish_time - self.start_time

    def backend_connect(self, replica_set_id, url):
        """
        BackendConnect event for current request
        """

        self.replica_set_ids.add(replica_set_id)
        self.pending_requests.append(BackendRequest(replica_set_id, url))
