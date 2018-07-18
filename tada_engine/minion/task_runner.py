# -*- coding: utf-8 -*-

from abc import ABC
import asyncio
from collections import deque
from concurrent.futures import ThreadPoolExecutor
import io
import hashlib
import queue
import uuid
import os

import aiofiles
import magic
import requests
import ujson
import uvloop


class AbstractTaskRunner(ABC):

    def __init__(self, task, _input, _output):
        self.task = task
        self._input = _input
        self._output = _output

        self.queue_in = None
        self.queue_out = None

    @staticmethod
    def _generate_key(data):
        if isinstance(data, bytes):
            data = data

        elif isinstance(data, str):
            data = data.encode("utf-8")

        else:
            data = ujson.dumps(data, sort_keys=True).encode("utf-8")

        # elif isinstance(data, dict):
        #     data = data.encode("utf-8")

        return hashlib.sha512(data).hexdigest()

    def _get_extension(self):
        return magic.from_file(self._input, mime=True)


class SimpleTaskRunner(AbstractTaskRunner):

    def __init__(self, task, _input, _output):
        super(SimpleTaskRunner, self).__init__(task, _input, _output)

        self.queue_in = deque()
        self.queue_out = deque()

    def read_input(self):
        with open(self._input, 'r') as file_resource:
            for line in file_resource.readlines():
                row = line.strip()
                self.queue_in.append(row)

    def run_task(self):
        for row in self.queue_in:
            result = self.task(row)
            self.queue_out.append(result)

    def write_output(self):
        with open(self._output, 'a') as file_resource:
            for result in self.queue_out:
                file_resource.write("{}\n".format(result))

    def execute_loop(self):
        self.read_input()
        self.run_task()
        self.write_output()

    def execute(self):
        if os.path.exists(self._output):
            os.remove(self._output)

        self.execute_loop()


class AsyncTaskRunner(AbstractTaskRunner):

    def __init__(self, task, _input, _output, pool_size=4):
        super(AsyncTaskRunner, self).__init__(task, _input, _output)

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        self.loop = asyncio.get_event_loop()
        self.pool_size = pool_size

        self.queue_in = asyncio.Queue()
        self.queue_out = asyncio.Queue()

    # def _open_file(self):
    #     with open(self._input, mode='rb', buffering=1024) as file_resource:
    #         yield file_resource.read(1024)
    #
    # def _open_http(self):
    #     pass

    """
    @staticmethod
    async def _readline(file_descriptor):
        yield file_descriptor.readline()

    async def _read_csv(self, future):
        async with aiofiles.open(self._input, mode='r') as file_descriptor:
            self.queue_in = await file_descriptor.readline()

    def _read_json(self):
        pass

    def _enqueue_input(self, data):
        key = self._generate_key(data)
        self.queue_in.put((key, data))
    """

    async def read_input(self):
        async with aiofiles.open(self._input, 'r') as file_resource:
            lines = await file_resource.readlines()
            for line in lines:
                row = line.strip()
                await self.queue_in.put(row)

        await self.queue_in.put(None)
        await self.queue_in.join()

    async def run_task(self):
        while True:
            row = await self.queue_in.get()

            if row is None:
                self.queue_in.task_done()
                break

            else:
                result = self.task(row)
                await self.queue_out.put(result)
                self.queue_in.task_done()

        await self.queue_out.put(None)
        await self.queue_out.join()

    async def write_output(self):
        while True:
            result = await self.queue_out.get()

            if result is None:
                self.queue_out.task_done()
                break

            else:
                async with aiofiles.open(self._output, 'a') as file_resource:
                    await file_resource.write("{}\n".format(result))

                self.queue_out.task_done()

    async def execute_loop(self):
        await asyncio.gather(
            self.read_input(),
            self.run_task(),
            self.write_output()
        )

    def execute(self):
        try:
            if os.path.exists(self._output):
                os.remove(self._output)

            self.loop.run_until_complete(self.execute_loop())

        finally:
            self.loop.close()


class ConcurrentTaskRunner(AbstractTaskRunner):

    def __init__(self, task, _input, _output, pool_size=4):
        super(ConcurrentTaskRunner, self).__init__(task, _input, _output)

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        self.loop = asyncio.get_event_loop()
        self.pool_size = pool_size

        self.queue_in = queue.Queue()
        self.queue_out = queue.Queue()

    # def _open_file(self):
    #     with open(self._input, mode='rb', buffering=1024) as file_resource:
    #         yield file_resource.read(1024)
    #
    # def _open_http(self):
    #     pass

    """
    @staticmethod
    async def _readline(file_descriptor):
        yield file_descriptor.readline()

    async def _read_csv(self, future):
        async with aiofiles.open(self._input, mode='r') as file_descriptor:
            self.queue_in = await file_descriptor.readline()

    def _read_json(self):
        pass

    def _enqueue_input(self, data):
        key = self._generate_key(data)
        self.queue_in.put((key, data))
    """

    def read_input(self):
        with open(self._input, 'r') as file_resource:
            for line in file_resource.readlines():
                row = line.strip()
                self.queue_in.put(row)

        self.queue_in.put(None)
        self.queue_in.join()

    def run_task(self):
        while True:
            row = self.queue_in.get()

            if row is None:
                self.queue_in.task_done()
                break

            else:
                result = self.task(row)
                self.queue_out.put(result)
                self.queue_in.task_done()

        self.queue_out.put(None)
        self.queue_out.join()

    def write_output(self):
        while True:
            result = self.queue_out.get()

            if result is None:
                self.queue_out.task_done()
                break

            else:
                with open(self._output, 'a') as file_resource:
                    file_resource.write("{}\n".format(result))

                self.queue_out.task_done()

    async def execute_loop(self):
        # Create a limited ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=self.pool_size) as thread_pool_executor:
            try:
                # Create a sub_loop
                sub_loop = asyncio.get_event_loop()

                tasks = [
                    sub_loop.run_in_executor(thread_pool_executor, self.read_input),
                    sub_loop.run_in_executor(thread_pool_executor, self.run_task),
                    sub_loop.run_in_executor(thread_pool_executor, self.write_output)
                ]

                await asyncio.wait(tasks)

            finally:
                thread_pool_executor.shutdown(wait=False)

    def execute(self):
        try:
            if os.path.exists(self._output):
                os.remove(self._output)

            self.loop.run_until_complete(self.execute_loop())

        finally:
            self.loop.close()
