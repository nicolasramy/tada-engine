# -*- coding: utf-8 -*-

import asyncio
import datetime
import logging
import random
import time

import zmq

from .. import Service


class MasterService(Service):
    NAME = "cowbell-engine-master"

    def __init__(self, config, is_daemon):
        # Get configuration values
        pid_file = config.get("cowbell-engine", "master_pid_file")
        log_file = config.get("cowbell-engine", "log_file")

        self.host = config.get("cowbell-engine", "host")
        self.frontend_port = config.getint("cowbell-engine", "frontend_port")

        try:
            log_level = getattr(logging, config.get("cowbell-engine", "log_level"))
        except AttributeError:
            log_level = logging.INFO

        self.context = zmq.Context()

        super(MasterService, self).__init__(self.NAME, pid_file, log_level, log_file, is_daemon=is_daemon)

    async def _client(self):
        self.logger.info("Start Master")
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("tcp://{}:{}".format(self.host, self.frontend_port))

        request_num = 1

        while True:
            data = {
                "request": request_num,
                "captured": str(datetime.datetime.utcnow())
            }
            self.socket.send_json(data)

            message = await self.socket.recv_json()
            self.logger.debug(message)

            waiting_time = random.randint(1, 3)
            self.logger.debug("Wait for {}s".format(waiting_time))
            time.sleep(waiting_time)

            request_num += 1

    def run(self):
        # loop = asyncio.get_event_loop()
        #
        # tasks = [
        #     asyncio.ensure_future(self._client())
        # ]
        #
        # loop.run_until_complete(asyncio.wait(tasks))
        # loop.close()

        self.logger.info("Start Master")
        self.socket = self.context.socket(zmq.REQ)

        address = "tcp://{}:{}".format(self.host, self.frontend_port)
        self.logger.debug("Connect to {}".format(address))
        self.socket.connect(address)

        self.logger.debug("Prepare before loop")
        request_num = 1

        while True:
            data = {
                "request": request_num,
                "captured": str(datetime.datetime.utcnow())
            }
            self.socket.send_json(data)

            message = self.socket.recv_json()
            self.logger.debug(message)

            waiting_time = random.randint(1, 3)
            self.logger.debug("Wait for {}s".format(waiting_time))
            time.sleep(waiting_time)

            request_num += 1

