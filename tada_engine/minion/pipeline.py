# -*- coding: utf-8 -*-

from abc import ABC
import hashlib
import os
import shelve
import shutil
import uuid

import plyvel
import ujson


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

        return hashlib.sha512(data)

    def _generate_string_key(self, data):
        key = self._generate_key(data)
        return key.hexdigest()

    def _generate_bytes_key(self, data):
        key = self._generate_key(data)
        return key.digest()


class InMemoryPipeline(AbstractPipeline):
    def __init__(self, name, hostname=DEFAULT_HOSTNAME, port=DEFAULT_PORT):
        super(InMemoryPipeline, self).__init__(name, hostname, port)

        self.filename = "/tmp/{}.db".format(self.uuid)

    def add(self, data):
        key = self._generate_string_key(data)

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


class LevelDBPipeline(AbstractPipeline):
    def __init__(self, name, hostname=DEFAULT_HOSTNAME, port=DEFAULT_PORT):
        super(LevelDBPipeline, self).__init__(name, hostname, port)

        self.filename = "/tmp/{}.db".format(self.uuid)

    @staticmethod
    def _encode(data):
        return ujson.dumps(data, sort_keys=True).encode("utf-8")

    @staticmethod
    def _decode(data):
        return ujson.loads(data)

    def add(self, data):
        key = self._generate_bytes_key(data)
        try:
            pipeline_resource = plyvel.DB(self.filename, create_if_missing=True)
            pipeline_resource.put(key, self._encode(data))
            response = True
        except (plyvel.Error, TypeError):
            response = False
        finally:
            pipeline_resource.close
            return response

    def remove(self, key):
        try:
            pipeline_resource = plyvel.DB(self.filename)
            if pipeline_resource.get(key):
                pipeline_resource.delete(key, sync=True)
                response = True
            else:
                response = False
        except (plyvel.Error, TypeError):
            response = False
        finally:
            pipeline_resource.close()
            return response

    def pop(self):
        try:
            pipeline_resource = plyvel.DB(self.filename)
            iterator = pipeline_resource.iterator(reverse=True)
            key, value = next(iterator)
            pipeline_resource.delete(key, sync=True)
            return key, self._decode(value)
        except (plyvel.Error, TypeError):
            return None, None

    def get(self, key):
        try:
            pipeline_resource = plyvel.DB(self.filename)
            response = self._decode(pipeline_resource.get(key))
        except (plyvel.Error, TypeError):
            response = None
        finally:
            pipeline_resource.close()
            return response

    def clear(self):
        if os.path.exists(self.filename):
            shutil.rmtree(self.filename, ignore_errors=True)
            return True
        else:
            return False
