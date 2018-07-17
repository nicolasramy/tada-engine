# -*- coding: utf-8 -*-

import asyncio
import io
from csv import DictReader

from aiofile import AIOFile, LineReader


class StreamProtocol(asyncio.Protocol):
    def __init__(self, loop, queue):
        self.loop = loop
        self.queue = queue

    def data_received(self, data):
        for message in data.decode().splitlines():
            self.queue.put_nowait(message.rstrip())

    def connection_lost(self, exc):
        self.loop.close()


class AsyncDictReader:
    def __init__(self, afp, **kwargs):
        self.buffer = io.BytesIO()
        self.file_reader = LineReader(
            afp, line_sep=kwargs.pop('line_sep', '\n'),
            chunk_size=kwargs.pop('chunk_size', 4096),
            offset=kwargs.pop('offset', 0),
        )
        self.reader = DictReader(
            io.TextIOWrapper(
                self.buffer,
                encoding=kwargs.pop('encoding', 'utf-8'),
                errors=kwargs.pop('errors', 'replace'),
            ), **kwargs,
        )

    async def __aiter__(self):
        header = await self.file_reader.readline()

        if header:
            self.buffer.write(header)

        return self

    async def __anext__(self):
        line = await self.file_reader.readline()

        if not line:
            raise StopAsyncIteration

        self.buffer.write(line)
        self.buffer.seek(0)

        try:
            result = next(self.reader)
        except StopIteration as e:
            raise StopAsyncIteration from e

        self.buffer.truncate(0)

        return result
