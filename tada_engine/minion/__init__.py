# -*- coding: utf-8 -*-

import asyncio
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
        log_file = config.get("tada-engine", "engine_log_file")

        self.host = config.get("tada-engine", "host")
        self.frontend_port = config.getint("tada-engine", "frontend_port")

        try:
            log_level = getattr(logging, config.get("tada-engine", "log_level"))
        except AttributeError:
            log_level = logging.INFO

        super(MinionService, self).__init__(self.NAME, pid_file, log_level, log_file, is_daemon=is_daemon)

        if not os.path.exists(config.get("tada-engine", "data_path")):
            os.mkdir(config.get("tada-engine", "data_path"))

        self.cache = plyvel.DB(config.get("tada-engine", "minion_cache"), create_if_missing=True)

    def _pre_exec(self):
        # Retrieve external resource
        # Cache locally this external resource
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as thread_pool_executor:
            pass

    def _exec(self):
        pass

    def _post_exec(self):
        pass

    async def _handle_request(self):
        self.logger.debug("Initialize Context and create a REQ's socket")
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)

        address = "tcp://{}:{}".format(self.host, self.frontend_port)
        self.logger.debug("Connect to {}".format(address))
        self.socket.connect(address)

        while True:
            # Ask for work
            self.socket.send_json(False)

            task = self.socket.recv_json()
            self.logger.debug(task)

            if task:

                # Add work in execution pool if possible
                task["status"] = random.choice(["RUNNING", "WAITING", "FAILURE"])

                # Response to Master about the state
                waiting_time = random.randint(1, 3)
                self.logger.debug("Wait for {}s".format(waiting_time))
                time.sleep(waiting_time)

                task["status"] = random.choice(["WAITING", "FAILURE"])
                task["captured"] = str(datetime.datetime.utcnow())

                self.socket.send_json(task)

                task = self.socket.recv_json()
                self.logger.debug(task)

            else:
                # Response to Master about the state
                waiting_time = random.randint(1, 3)
                self.logger.debug("Wait for {}s".format(waiting_time))
                time.sleep(waiting_time)



    def run(self):
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        loop = asyncio.get_event_loop()

        tasks = [
            asyncio.ensure_future(self._handle_request())
        ]

        try:
            loop.run_until_complete(asyncio.wait(tasks))

        except KeyboardInterrupt:
            pass

        finally:
            loop.close()

