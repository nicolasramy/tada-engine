# -*- coding: utf-8 -*-

import aiofiles
import asyncio
from concurrent.futures import ThreadPoolExecutor
import io
import hashlib
from queue import Queue
import uuid
import os

import magic
import requests
import ujson
import uvloop


class TaskRunner:

    def __init__(self, task, _input, _output, schedule=None, priority=0, pool_size=4):
        self.task = task
        self._input = _input
        self._output = _output
        self.schedule = schedule
        self.priority = priority
        self.pool_size = pool_size

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        self.loop = asyncio.get_event_loop()

        self.queue_in = asyncio.Queue(pool_size)
        self.queue_out = asyncio.Queue(pool_size)

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
        print("read_input")
        async with aiofiles.open(self._input, 'r') as file_resource:
            lines = await file_resource.readlines()
            for line in lines:
                row = line.strip()
                print("read_input: {}".format(row))
                await self.queue_in.put(row)

        await self.queue_in.put(None)
        await self.queue_in.join()

    async def run_task(self):
        print("run_task")

        while True:
            row = await self.queue_in.get()

            if row is None:
                self.queue_in.task_done()
                break

            else:
                result = self.task(row)
                print("run_task: {} --> {}".format(row, result))
                await self.queue_out.put(result)
                self.queue_in.task_done()

        await self.queue_out.put(None)
        await self.queue_out.join()

    async def write_output(self):
        print("write_output")

        while True:
            result = await self.queue_out.get()

            if result is None:
                self.queue_out.task_done()
                break

            else:
                print("write_output: {}".format(result))

                # TODO: Write output
                async with aiofiles.open(self._output, 'a') as file_resource:
                    await file_resource.write("{}\n".format(result))

                await asyncio.sleep(0.001)
                self.queue_out.task_done()

    async def execute_loop(self):
        await asyncio.gather(
            self.loop.create_task(self.read_input()),
            self.loop.create_task(self.run_task()),
            self.loop.create_task(self.write_output())
        )

    def execute(self):
        try:
            if os.path.exists(self._output):
                os.remove(self._output)
            self.loop.run_until_complete(self.execute_loop())

        finally:
            self.loop.close()
