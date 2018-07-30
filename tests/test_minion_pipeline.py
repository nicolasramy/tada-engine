# -*- coding: utf-8 -*-

import os
import unittest

from tada_engine.minion import AbstractPipeline, InMemoryPipeline, FilePipeline


class AbstractPipelineTest(unittest.TestCase):

    def test_hash_string(self):
        pipeline = AbstractPipeline('hello')
        self.assertEqual(
            pipeline._generate_key('Hello World'),
            '2c74fd17edafd80e8447b0d46741ee243b7eb74dd2149a0ab1b9246fb30382f27e853d8585719e0e67cbda0daa8f51671064615d64'
            '5ae27acb15bfb1447f459b'
        )


class InMemoryPipelineTest(unittest.TestCase):
    def test_add(self):
        pipeline = InMemoryPipeline('test_pipeline')
        self.assertTrue(pipeline.add({"message": "Hello World"}))
        self.assertTrue(pipeline.clear())

    def test_remove(self):
        pipeline = InMemoryPipeline('test_pipeline')
        pipeline.add({"message1": "Hello World"})
        pipeline.add({"message2": "Bonjour le monde"})
        pipeline.add({"message3": "Hola Mundo"})

        key_to_remove = pipeline._generate_key({"message2": "Bonjour le monde"})

        self.assertTrue(pipeline.remove(key_to_remove))
        self.assertFalse(pipeline.remove(key_to_remove))
        self.assertTrue(pipeline.clear())

    def test_pop(self):
        pipeline = InMemoryPipeline('test_pipeline')
        pipeline.add({"message1": "Hello World"})
        pipeline.add({"message2": "Bonjour le monde"})
        pipeline.add({"message3": "Hola Mundo"})

        data_popped = {"message3": "Hola Mundo"}
        key_popped = pipeline._generate_key(data_popped)

        self.assertEqual(pipeline.pop(), (key_popped, data_popped))
        self.assertTrue(pipeline.clear())

    def test_get(self):
        pipeline = InMemoryPipeline('test_pipeline')
        pipeline.add({"message1": "Hello World"})
        pipeline.add({"message2": "Bonjour le monde"})
        pipeline.add({"message3": "Hola Mundo"})

        data = {"message1": "Hello World"}
        key_to_get = pipeline._generate_key(data)

        self.assertEqual(pipeline.get(key_to_get), data)
        self.assertTrue(pipeline.clear())
