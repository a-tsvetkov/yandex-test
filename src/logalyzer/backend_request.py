# -*- coding:utf-8 -*-


class BackendRequest(object):

    def __init__(self, replica_id, url):
        self.replica_id = replica_id
        self.url = url
