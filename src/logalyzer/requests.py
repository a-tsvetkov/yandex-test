# -*- coding:utf-8 -*-


class BackendRequest(object):

    def __init__(self, replica_set_id, url):
        self.replica_set_id = replica_set_id
        self.url = url


class ClientRequest(object):

    def __init__(self, id, start_time, finish_time=None):
        self.id = id
        self.start_time = start_time
        self.finish_time = finish_time

        self.replica_set_ids = set()
        self.pending_requests = {}

    @property
    def duration(self):
        """
        Request duration, None if request not finished
        """
        if self.finish_time is None:
            return

        return self.finish_time - self.start_time

    def last_request_url(self, replica_set_id):
        """
        Get url for last request made to specified replica set
        """

        return self.pending_requests[replica_set_id].url

    def backend_connect(self, replica_set_id, url):
        """
        BackendConnect event for current request
        """

        self.replica_set_ids.add(replica_set_id)
        self.pending_requests[replica_set_id] = BackendRequest(replica_set_id, url)

    def backend_error(self, replica_set_id):
        """
        BackendError event for current request
        """

        del self.pending_requests[replica_set_id]
