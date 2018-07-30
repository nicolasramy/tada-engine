# -*- coding: utf-8 -*-

import os
import unittest

from tada_engine.minion import AbstractTaskRunner, SimpleTaskRunner, AsyncTaskRunner, ConcurrentTaskRunner

from . import add


class AbstractTaskRunnerTest(unittest.TestCase):

    INPUT = 'tests/input.csv'
    OUTPUT = 'tests/output.csv'
    TASK = add

    def test_get_extension_input(self):
        task_runner = AbstractTaskRunner(self.TASK, self.INPUT, self.OUTPUT)
        self.assertEqual(
            task_runner._get_extension(),
            'text/plain'
        )


class SimpleTaskRunnerTest(unittest.TestCase):

    INPUT = 'tests/input.csv'
    OUTPUT = 'tests/output.csv'
    TASK = add

    def test_execute(self):
        task_runner = SimpleTaskRunner(self.TASK, self.INPUT, self.OUTPUT)

        task_runner.execute()

        self.assertEqual(
            os.path.getsize(self.OUTPUT),
            3277
        )


class AsyncTaskRunnerTest(unittest.TestCase):

    INPUT = 'tests/input.csv'
    OUTPUT = 'tests/output.csv'
    TASK = add

    def test_execute(self):
        task_runner = AsyncTaskRunner(self.TASK, self.INPUT, self.OUTPUT)

        task_runner.execute()

        self.assertEqual(
            os.path.getsize(self.OUTPUT),
            3277
        )


class ConcurrentTaskRunnerTest(unittest.TestCase):

    INPUT = 'tests/input.csv'
    OUTPUT = 'tests/output.csv'
    TASK = add

    def test_execute(self):
        task_runner = ConcurrentTaskRunner(self.TASK, self.INPUT, self.OUTPUT)

        task_runner.execute()

        self.assertEqual(
            os.path.getsize(self.OUTPUT),
            3277
        )

