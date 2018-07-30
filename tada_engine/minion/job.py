# -*- coding: utf-8 -*-

from enum import Enum


class Job(Enum):

    WAITING = 1
    PENDING = 2
    RUNNING = 3
    SUCCESS = 4
    FAILURE = 5

    TRANSITIONS = {
        WAITING: [],
        PENDING: [],
        RUNNING: [],
        SUCCESS: [],
        FAILURE: []
    }

    def __init__(self):
        self.current_state = self.WAITING
        self.previous_state = None

    def validate_input(self):
        pass

    def validate_output(self):
        pass

    def run(self):
        pass


