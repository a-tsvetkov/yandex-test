# -*- coding:utf-8 -*-


class BackendRequest(object):

    def __init__(self, replica_set_id, host):
        self.replica_set_id = replica_set_id
        self.host = host


class ClientRequest(object):

    def __init__(self, id, start_time, finish_time=None):
        self.id = id
        self.start_time = start_time
        self.finish_time = finish_time

        self.started_replica_sets = set()
        self.completed_replica_sets = set()
        self.pending_requests = {}

    @property
    def duration(self):
        """
        Request duration, None if request not finished
        """
        if self.finish_time is None:
            return

        return self.finish_time - self.start_time

    @property
    def incomplete(self):
        return (
            len(self.pending_requests) > 0 or
            len(self.started_replica_sets - self.completed_replica_sets) > 0
        )

    def last_request_host(self, replica_set_id):
        """
        Get host for last request made to specified replica set
        """

        return self.pending_requests[replica_set_id].host

    def finish_request(self, replica_set_id):
        """
        BackendError event for current request
        """

        del self.pending_requests[replica_set_id]

    def backend_connect(self, replica_set_id, host):
        """
        BackendConnect event for current request
        """
        request = BackendRequest(replica_set_id, host)
        self.started_replica_sets.add(replica_set_id)
        self.pending_requests[replica_set_id] = request

    def backend_ok(self, replica_set_id):
        self.finish_request(replica_set_id)
        self.completed_replica_sets.add(replica_set_id)

    def backend_error(self, replica_set_id):
        self.finish_request(replica_set_id)
