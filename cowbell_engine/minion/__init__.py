# -*- coding: utf-8 -*-

import logging
import sys
import time

from .. import Program, Service


DEFAULT_NAME = 'cowbell-engine-minion'
DEFAULT_LOG_FILENAME = '/var/log/cowbell-engine-minion.log'
DEFAULT_PID_FILENAME = '/var/run/cowbell-engine-minion.pid'

DEFAULT_LOGGING_LEVEL = logging.DEBUG

DEFAULT_PROXY_FRONTEND_PORT = 5500
DEFAULT_PROXY_BACKEND_PORT = 5600
DEFAULT_PROXY_MONITORING_PORT = 5700


class Minion:
    DEFAULT_NAME = 'cowbell-engine-proxy'
    DEFAULT_LOG_FILENAME = '/var/log/cowbell-engine-minion.log'
    DEFAULT_PID_FILENAME = '/var/run/cowbell-engine-proxy.pid'

    DEFAULT_LOGGING_LEVEL = logging.DEBUG

    DEFAULT_PROXY_FRONTEND_PORT = 5500
    DEFAULT_PROXY_BACKEND_PORT = 5600
    DEFAULT_PROXY_MONITORING_PORT = 5700

    def run(self):
        sys.stdout.write('Starting Minion')
        while True:
            time.sleep(3)
            sys.stdout.write('eh')


class MinionProgram(Minion, Program):
    def __init__(self, name=DEFAULT_NAME, pid_file=DEFAULT_PID_FILENAME,
                 stdin='/dev/null', stdout=DEFAULT_LOG_FILENAME, stderr=DEFAULT_LOG_FILENAME):

        super(MinionProgram, self).__init__(name, pid_file, stdin, stdout, stderr)


class MinionService(Minion, Service):

    def __init__(self, name=DEFAULT_NAME, pid_file=DEFAULT_PID_FILENAME,
                 stdin='/dev/null', stdout=DEFAULT_LOG_FILENAME, stderr=DEFAULT_LOG_FILENAME):

        super(MinionService, self).__init__(name, pid_file, stdin, stdout, stderr)
