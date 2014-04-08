# -*- coding:utf-8 -*-
from collections import defaultdict

from utils import get_host


class ReplicaSetStat(object):

    def __init__(self, id):
        self.id = id

        self.backends_dict = {}

    @property
    def backends(self):
        """
        Returns list of backend names
        """

        return self.backends_dict.keys()

    def get_backend(self, host):
        """
        Tries to find backend by its host
        """

        return self.backends_dict.get(host)

    def get_backend_for_url(self, url):
        """
        Return backend for request url
        """

        return self.get_backend(get_host(url))

    def backend_connect(self, url):
        """
        Processes BackendConnect event for this replica set
        """

        backend = self.get_backend_for_url(url)
        if backend is None:
            backend = self.add_backend(get_host(url))

        backend.request_count += 1

    def backend_error(self, url, error):
        """
        Logs an error to corresponding backend stat
        """

        backend = self.get_backend_for_url(url)
        backend.add_error(error)

    def add_backend(self, host):
        """
        Add new backend stat to this replica set
        """

        backend = BackendStat(host)
        self.backends_dict[host] = backend
        return backend


class BackendStat(object):

    def __init__(self, host):
        self.host = host

        self.request_count = 0
        self.errors = defaultdict(int)

    def add_error(self, error):
        """
        Logs backeb error
        """

        self.errors[error] += 1
