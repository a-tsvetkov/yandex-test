# -*- coding:utf-8 -*-
import heapq


def heap_percentile(p, heap, key=None):
    """
    Calculate percentile
    """

    (nth, p) = (heapq.nsmallest, p) if p <= 50 else (heapq.nlargest, 100 - p)
    return nth(max(1, int(len(heap) * p / 100.0 + 0.5)), heap, key=key)[-1]


def get_host(url):
    """
    Get host from url
    """

    return url.split("/", 3)[2]  # Uglier than urlparse but faster
