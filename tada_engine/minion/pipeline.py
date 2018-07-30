# -*- coding: utf-8 -*-

from abc import ABC
import asyncio
from collections import deque
from concurrent.futures import ThreadPoolExecutor
import dbm
import hashlib
import io
from multiprocessing import Process
import os
import pickle
import shelve
import socket
import tempfile
import uuid

import plyvel
import ujson
import zmq


DEFAULT_HOSTNAME = 'localhost'
DEFAULT_PORT = 5100


class AbstractPipeline(ABC):

    def __init__(self, name, hostname=DEFAULT_HOSTNAME, port=DEFAULT_PORT):
        self.name = name
        self.uuid = uuid.uuid5(uuid.NAMESPACE_DNS, self.name)
        self.hostname = hostname
        self.port = port

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


class InMemoryPipeline(AbstractPipeline):
    def __init__(self, name, hostname=DEFAULT_HOSTNAME, port=DEFAULT_PORT):
        super(InMemoryPipeline, self).__init__(name, hostname, port)

        self.filename = "/tmp/{}.db".format(self.name)

        # if os.path.exists(self.filename):

    def add(self, data):
        key = self._generate_key(data)

        with shelve.open(self.filename) as pipeline_resource:
            if key in pipeline_resource:
                return False
            else:
                pipeline_resource[key] = data
                return True

    def remove(self, key):
        with shelve.open(self.filename) as pipeline_resource:
            if key in pipeline_resource:
                del pipeline_resource[key]
                return True
            else:
                return False

    def pop(self):
        with shelve.open(self.filename) as pipeline_resource:
            try:
                data = pipeline_resource.popitem()
                return data
            except KeyError:
                return False

    def get(self, key):
        with shelve.open(self.filename) as pipeline_resource:
            if key in pipeline_resource:
                data = pipeline_resource.pop(key)
                return data
            else:
                return None

    def clear(self):
        with shelve.open(self.filename) as pipeline_resource:
            pipeline_resource.clear()
            return True


class FilePipeline(AbstractPipeline):
    def __init__(self, name):
        super(FilePipeline, self).__init__(name)

        self.pipe = tempfile.NamedTemporaryFile(prefix='pipe_')


class LevelDBPipeline(AbstractPipeline):
    def __init__(self, name, address='/tmp/tada-engine'):
        super(LevelDBPipeline, self).__init__(name, address)

        self.pipe = plyvel.DB(self.address, create_if_missing=True)


        # self.cache = plyvel.DB(self.cache_path, create_if_missing=True)
