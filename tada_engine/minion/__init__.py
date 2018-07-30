# -*- coding: utf-8 -*-

import asyncio
import configparser
from concurrent.futures import ThreadPoolExecutor
import datetime
import logging
import os
import random
import time
import traceback
import sys

import plyvel
import uvloop
import zmq

from .. import Logger, Service
# from ..core import multiprocessing_pool_initializer
from .pipeline import AbstractPipeline, InMemoryPipeline, LevelDBPipeline
from .task_runner import AbstractTaskRunner, SimpleTaskRunner, AsyncTaskRunner, ConcurrentTaskRunner


class MinionService(Service):
    NAME = "tada-engine-minion"

    def __init__(self, config, is_daemon):
        # Get configuration values
        pid_file = config.get("tada-engine", "minion_pid_file")
        log_file = config.get("tada-engine", "engine_log_file")

        self.host = config.get("tada-engine", "host")
        self.frontend_port = config.getint("tada-engine", "frontend_port")

        self.max_workers = config.getint("tada-engine", "max_workers")

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
        with ThreadPoolExecutor(max_workers=4) as thread_pool_executor:
            pass

    def _exec(self):
        pass

    def _post_exec(self):
        pass

    def _handle_request(self, worker_id):
        self.logger.debug("Initialize Context and create a REQ's socket for worker {}".format(worker_id))
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)

        address = "tcp://{}:{}".format(self.host, self.frontend_port)
        self.logger.debug("Connect worker-{} to {}".format(worker_id, address))
        self.socket.connect(address)

        try:
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
                self.logger.debug("Worker-{} Wait for {}s".format(worker_id, waiting_time))
                time.sleep(waiting_time)

            exit_code = 1

        except Exception as error:
            self.logger.critical(error)
            self.logger.debug(traceback.format_exc())
            exit_code = -1

        except KeyboardInterrupt:
            self.logger.debug("Ask for interruption in _handle_request")
            exit_code = 0

        finally:
            self.socket.close()
            return exit_code

    def run(self):
        # Create a limited ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=self.max_workers) as thread_pool_executor:
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            main_loop = asyncio.get_event_loop()

            try:
                # main_loop.run_until_complete(self.main(thread_pool_executor))

                futures = [
                    main_loop.run_in_executor(thread_pool_executor, self._handle_request, worker_id)
                    for worker_id in range(self.max_workers)
                ]

                # completed, pending = await asyncio.wait(futures)
                # self.logger.debug(pending)
                # results = [coroutine.result() for coroutine in completed]
                main_loop.run_until_complete(asyncio.gather(*futures))
                # self.logger.debug(results)

            except Exception as error:
                self.logger.critical(error)
                self.logger.debug(traceback.format_exc())

            except KeyboardInterrupt:
                self.logger.debug("Ask for interruption in _handle_request")

            finally:
                self.logger.debug("Kill the main_loop")
                main_loop.close()
                self.logger.debug("Kill the ThreadPoolExecutor")
                thread_pool_executor.shutdown(wait=False)
                self.logger.info("Exiting")


__all__ = [
    'AbstractTaskRunner',
    'SimpleTaskRunner',
    'AsyncTaskRunner',
    'ConcurrentTaskRunner',
    'AbstractPipeline',
    'InMemoryPipeline',
    'LevelDBPipeline'
]
