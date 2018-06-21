# -*- coding: utf-8 -*-

import logging
import sys
import time

from .. import Program, Service


DEFAULT_NAME = 'cowbell-engine-master'
DEFAULT_LOG_FILENAME = '/var/log/cowbell-engine-master.log'
DEFAULT_PID_FILENAME = '/var/run/cowbell-engine-master.pid'

DEFAULT_LOGGING_LEVEL = logging.DEBUG

DEFAULT_PROXY_FRONTEND_PORT = 5500
DEFAULT_PROXY_BACKEND_PORT = 5600
DEFAULT_PROXY_MONITORING_PORT = 5700


class Master:
    DEFAULT_NAME = 'cowbell-engine-proxy'
    DEFAULT_LOG_FILENAME = '/var/log/cowbell-engine-master.log'
    DEFAULT_PID_FILENAME = '/var/run/cowbell-engine-proxy.pid'

    DEFAULT_LOGGING_LEVEL = logging.DEBUG

    DEFAULT_PROXY_FRONTEND_PORT = 5500
    DEFAULT_PROXY_BACKEND_PORT = 5600
    DEFAULT_PROXY_MONITORING_PORT = 5700

    def run(self):
        sys.stdout.write('Starting Master')
        while True:
            time.sleep(3)
            sys.stdout.write('eh')


class MasterProgram(Master, Program):
    def __init__(self, name=DEFAULT_NAME, pid_file=DEFAULT_PID_FILENAME,
                 stdin='/dev/null', stdout=DEFAULT_LOG_FILENAME, stderr=DEFAULT_LOG_FILENAME):

        super(MasterProgram, self).__init__(name, pid_file, stdin, stdout, stderr)


class MasterService(Master, Service):

    def __init__(self, name=DEFAULT_NAME, pid_file=DEFAULT_PID_FILENAME,
                 stdin='/dev/null', stdout=DEFAULT_LOG_FILENAME, stderr=DEFAULT_LOG_FILENAME):

        super(MasterService, self).__init__(name, pid_file, stdin, stdout, stderr)
