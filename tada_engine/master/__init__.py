# -*- coding: utf-8 -*-

import asyncio
import datetime
import logging

import uvloop
import zmq
from zmq.devices.monitoredqueuedevice import ThreadMonitoredQueue
from zmq.utils.strtypes import asbytes

from .. import Service


class MasterService(Service):
    NAME = "tada-engine-master"

    def __init__(self, config, is_daemon):
        # Get configuration values
        pid_file = config.get("tada-engine", "master_pid_file")
        log_file = config.get("tada-engine", "log_file")

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

        self.logger.info("Start Proxy/MonitoredQueue")
        self.device.start()

    async def _monitor(self):
        self.logger.info("Start Proxy/Monitor")
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect("tcp://{}:{}".format(self.host, self.monitoring_port))
        self.socket.setsockopt(zmq.SUBSCRIBE, b"")

        while True:
            # All messages sent on mons will be multipart,
            # the first part being the prefix corresponding to the socket that received the message.
            data = self.socket.recv_multipart()
            self.logger.debug(data)

            # TODO: Define what to do on monitoring message

    async def _scheduler(self):
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

            request_num += 1

    def run(self):
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        loop = asyncio.get_event_loop()

        tasks = [
            asyncio.ensure_future(self._monitored_queue()),
            asyncio.ensure_future(self._monitor()),
            asyncio.ensure_future(self._scheduler())
        ]

        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()



