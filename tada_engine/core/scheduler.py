# -*- coding: utf-8 -*-

import asyncio

import ujson
import uvloop


class Scheduler:

    def __init__(self):
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        self.loop = asyncio.get_event_loop()

    @staticmethod
    def _to_str(key):
        return str(key)

    @staticmethod
    def _to_bytes(key):
        return bytes(key, "utf-8")

    @staticmethod
    def encode_task(data):
        return ujson.dumps(data)

    @staticmethod
    def decode_task(data):
        return ujson.loads(data)

    def change_status(self, key, new_status):
        if isinstance(key, bytes):
            str_key = self._to_str(key)
        else:
            str_key = key

        old_status, identifier = str_key.split("/", maxsplit=1)

        if old_status != new_status:
            return self._to_bytes("{}/{}".format(new_status, identifier))

        return key
