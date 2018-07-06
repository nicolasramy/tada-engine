# -*- coding: utf-8 -*-

import concurrent.futures
import datetime
import logging
import os
import random
import time

import plyvel
import uvloop
import zmq

from .. import Service

# TODO: https://stackoverflow.com/questions/43124340/python-3-6-coroutine-was-never-awaited


class MinionService(Service):
    NAME = "tada-engine-minion"

    def __init__(self, config, is_daemon):
        # Get configuration values
        pid_file = config.get("tada-engine", "minion_pid_file")
        log_file = config.get("tada-engine", "admin_log_file")

        self.host = config.get("tada-engine", "host")
        self.backend_port = config.getint("tada-engine", "backend_port")

        try:
            log_level = getattr(logging, config.get("tada-engine", "log_level"))
        except AttributeError:
            log_level = logging.INFO

        super(MinionService, self).__init__(self.NAME, pid_file, log_level, log_file, is_daemon=is_daemon)

        if not os.path.exists(config.get("tada-engine", "data_path")):
            os.mkdir(config.get("tada-engine", "data_path"))

        self.cache = plyvel.DB(config.get("tada-engine", "minion_cache"))

    def _pre_exec(self):
        # Retrieve external resource
        # Cache locally this external resource
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as thread_pool_executor:
            pass

    def _exec(self):
        pass

    def _post_exec(self):
        pass

    def run(self):
        self.logger.debug("Initialize Context and create a REP's socket")
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)

        self.logger.debug("Connect to Proxy")
        self.socket.connect("tcp://{}:{}".format(self.host, self.backend_port))

        # TODO:
        # - ThreadPool Executor
        # - notifications / results layer

        while True:
            message = self.socket.recv_json()
            self.logger.debug(message)

            data = {
                "received": message,
                "captured": str(datetime.datetime.utcnow())
            }
            self.socket.send_json(data)

            waiting_time = random.randint(1, 3)
            self.logger.debug("Wait for {}s".format(waiting_time))
            time.sleep(waiting_time)
