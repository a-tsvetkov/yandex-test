# -*- coding:utf-8 -*-


class BackendRequest(object):

    def __init__(self, replica_set_id, url):
        self.replica_set_id = replica_set_id
        self.url = url
