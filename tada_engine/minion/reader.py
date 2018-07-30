# -*- coding: utf-8 -*-

import asyncio
import io
from csv import DictReader

import aiofiles


class StreamProtocol(asyncio.Protocol):
    def __init__(self, loop, queue):
        self.loop = loop
        self.queue = queue

    def data_received(self, data):
        for message in data.decode().splitlines():
            self.queue.put_nowait(message.rstrip())

    def connection_lost(self, exc):
        self.loop.close()
