# -*- coding: utf-8 -*-

import hashlib
import unittest

from tada_engine.minion import AbstractPipeline, InMemoryPipeline, LevelDBPipeline


class AbstractPipelineTest(unittest.TestCase):
    def setUp(self):
        self.pipeline = AbstractPipeline('hello')

    def test_generate_key(self):
        self.assertIsInstance(self.pipeline._generate_key('Hello World'), hashlib._hashlib.HASH)

    def test_generate_string_key(self):
        string_key = hashlib.sha512(b'Hello World').hexdigest()
        self.assertEqual(self.pipeline._generate_string_key('Hello World'), string_key)

    def test_generate_bytes_key(self):
        bytes_key = hashlib.sha512(b'Hello World').digest()
        self.assertEqual(self.pipeline._generate_bytes_key('Hello World'), bytes_key)


class InMemoryPipelineTest(unittest.TestCase):
    def setUp(self):
        self.pipeline = InMemoryPipeline('inmemory_test_pipeline')

    def tearDown(self):
        self.pipeline.clear()

    def test_add(self):
        self.assertTrue(self.pipeline.add({"message": "Hello World"}))

    def test_remove(self):
        self.pipeline.add({"message1": "Hello World"})
        self.pipeline.add({"message2": "Bonjour le monde"})
        self.pipeline.add({"message3": "Hola Mundo"})

        key_to_remove = self.pipeline._generate_string_key({"message2": "Bonjour le monde"})

        self.assertTrue(self.pipeline.remove(key_to_remove))
        self.assertFalse(self.pipeline.remove(key_to_remove))

    def test_pop(self):
        self.pipeline.add({"message1": "Hello World"})
        self.pipeline.add({"message2": "Bonjour le monde"})
        self.pipeline.add({"message3": "Hola Mundo"})

        data_popped = {"message3": "Hola Mundo"}
        key_popped = self.pipeline._generate_string_key(data_popped)

        self.assertEqual(self.pipeline.pop(), (key_popped, data_popped))

    def test_get(self):
        self.pipeline.add({"message1": "Hello World"})
        self.pipeline.add({"message2": "Bonjour le monde"})
        self.pipeline.add({"message3": "Hola Mundo"})

        data = {"message1": "Hello World"}
        key_to_get = self.pipeline._generate_string_key(data)

        self.assertEqual(self.pipeline.get(key_to_get), data)


class LevelDBPipelineTest(unittest.TestCase):
    def setUp(self):
        self.pipeline = LevelDBPipeline('leveldb_test_pipeline')

    def tearDown(self):
        self.pipeline.clear()

    def test_add(self):
        self.assertTrue(self.pipeline.add({"message": "Hello World"}))

    def test_remove(self):
        self.pipeline.add({"message1": "Hello World"})
        self.pipeline.add({"message2": "Bonjour le monde"})
        self.pipeline.add({"message3": "Hola Mundo"})

        key_to_remove = self.pipeline._generate_bytes_key({"message2": "Bonjour le monde"})

        self.assertTrue(self.pipeline.remove(key_to_remove))
        self.assertFalse(self.pipeline.remove(key_to_remove))

    def test_pop(self):
        self.pipeline.add({"message1": "Hello World"})
        self.pipeline.add({"message2": "Bonjour le monde"})
        self.pipeline.add({"message3": "Hola Mundo"})

        data_popped = {"message3": "Hola Mundo"}
        key_popped = self.pipeline._generate_bytes_key(data_popped)

        self.assertEqual(self.pipeline.pop(), (key_popped, data_popped))

    def test_get(self):
        self.pipeline.add({"message1": "Hello World"})
        self.pipeline.add({"message2": "Bonjour le monde"})
        self.pipeline.add({"message3": "Hola Mundo"})

        data = {"message1": "Hello World"}
        key_to_get = self.pipeline._generate_bytes_key(data)

        self.assertEqual(self.pipeline.get(key_to_get), data)
