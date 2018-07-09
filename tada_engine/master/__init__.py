# -*- coding: utf-8 -*-

import asyncio
import concurrent.futures.thread
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime
import logging
import os

import uvloop
import plyvel
import ujson
import zmq
from zmq.devices.monitoredqueuedevice import ThreadMonitoredQueue
from zmq.utils.strtypes import asbytes

from .. import Service
from ..core import Scheduler


class MasterService(Service, Scheduler):
    NAME = "tada-engine-master"

    def __init__(self, config, is_daemon):
        # Get configuration values
        pid_file = config.get("tada-engine", "master_pid_file")
        log_file = config.get("tada-engine", "engine_log_file")

        self.host = config.get("tada-engine", "host")
        self.frontend_port = config.getint("tada-engine", "frontend_port")
        self.backend_port = config.getint("tada-engine", "backend_port")
        self.monitoring_port = config.getint("tada-engine", "monitoring_port")

        try:
            log_level = getattr(logging, config.get("tada-engine", "log_level"))
        except AttributeError:
            log_level = logging.INFO

        self.context = zmq.Context()

        super(MasterService, self).__init__(self.NAME, pid_file, log_level, log_file, is_daemon=is_daemon)

        if not os.path.exists(config.get("tada-engine", "data_path")):
            os.mkdir(config.get("tada-engine", "data_path"))

        self.cache_path = config.get("tada-engine", "master_cache")

    async def _monitored_queue(self):
        in_prefix = asbytes("in")
        out_prefix = asbytes("out")

        self.device = ThreadMonitoredQueue(zmq.XREP, zmq.XREQ, zmq.PUB, in_prefix, out_prefix)

        in_address = "tcp://{}:{}".format(self.host, self.frontend_port)
        self.logger.debug("Bind IN: {}".format(in_address))
        self.device.bind_in(in_address)

        out_address = "tcp://{}:{}".format(self.host, self.backend_port)
        self.logger.debug("Bind OUT: {}".format(out_address))
        self.device.bind_out(out_address)

        mon_address = "tcp://{}:{}".format(self.host, self.monitoring_port)
        self.logger.debug("Bind MON: {}".format(mon_address))
        self.device.bind_mon(mon_address)

        self.device.setsockopt_in(zmq.RCVHWM, 1)
        self.device.setsockopt_out(zmq.SNDHWM, 1)

        self.logger.info("Start MonitoredQueue")
        self.device.start()

    async def _supervisor(self):
        # TODO: Create and handle PUB/SUB
        self.logger.info("Start Supervisor")
        while True:
            pass

    def get_waiting_task(self):
        # Retrieve tasks to execute
        self.cache = plyvel.DB(self.cache_path, create_if_missing=True)
        with self.cache.snapshot() as cache_snapshot:
            for identifier, description in cache_snapshot.iterator(prefix=b"WAITING/"):
                self.cache.close()
                yield (identifier, description)

    async def _scheduler(self):
        self.logger.info("Start Scheduler")
        self.socket = self.context.socket(zmq.REP)

        address = "tcp://{}:{}".format(self.host, self.backend_port)
        self.logger.debug("Connect to {}".format(address))
        self.socket.connect(address)

        self.logger.debug("Scheduler loop...")

        while True:
            # Receive work request
            task = self.socket.recv_json()

            self.logger.debug("Task received: {}".format(task))

            if not task:
                try:
                    self.logger.debug("Empty task")

                    identifier, description = next(self.get_waiting_task())

                    self.logger.debug("Job: {}".format(identifier))

                    # Remove current identifier
                    self.cache = plyvel.DB(self.cache_path, create_if_missing=True)
                    self.cache.delete(identifier)
                    self.cache.close()

                    # Load task description
                    task = self.decode_task(description)

                    # Change task status to PENDING
                    identifier = self.change_status(identifier, "PENDING")
                    self.cache = plyvel.DB(self.cache_path, create_if_missing=True)
                    self.cache.put(identifier, description)
                    self.cache.close()

                    task["uid"] = str(identifier)
                    # self.logger.info(type(task))
                    # self.logger.info(task)

                    # Send task to execute to worker
                    # self.socket.send_json(task)

                except StopIteration:
                    pass

            else:
                self.logger.debug("Do something else")
                identifier = task["uid"]
                identifier = self.change_status(identifier, task["status"])

                task = self.encode_task(task)

                self.cache = plyvel.DB(self.cache_path, create_if_missing=True)
                self.cache.put(identifier, self._to_bytes(task))
                self.cache.close()

            self.socket.send_json(task)

            # Add sleep?

    def run(self):
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        loop = asyncio.get_event_loop()

        tasks = [
            asyncio.ensure_future(self._monitored_queue()),
            asyncio.ensure_future(self._scheduler()),
            # asyncio.ensure_future(self._supervisor())
        ]

        try:
            loop.run_until_complete(asyncio.wait(tasks))

        except KeyboardInterrupt:
            pass

        finally:
            loop.close()
