# -*- coding: utf-8 -*-

from enum import Enum


class Job(Enum):

    WAITING = 1
    PENDING = 2
    RUNNING = 3
    SUCCESS = 4
    FAILURE = 5

    def __init__(self):
        pass

    def validate_input(self):
        pass

    def validate_output(self):
        pass

    def run(self):
        pass
