# -*- coding: utf-8 -*-

import signal

from .scheduler import Scheduler


def multiprocessing_pool_initializer():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


__all__ = ["Scheduler"]
