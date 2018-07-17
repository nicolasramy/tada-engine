# -*- coding: utf-8 -*-

import os
import unittest

from tada_engine.minion import TaskRunner

from . import add


class TaskRunnerTest(unittest.TestCase):

    INPUT = 'tests/input.csv'
    OUTPUT = 'tests/output.csv'
    TASK = add

    def test_hash_string(self):
        task_runner = TaskRunner(self.TASK, self.INPUT, self.OUTPUT)
        self.assertEqual(
            task_runner._generate_key('Hello World'),
            '2c74fd17edafd80e8447b0d46741ee243b7eb74dd2149a0ab1b9246fb30382f27e853d8585719e0e67cbda0daa8f51671064615d64'
            '5ae27acb15bfb1447f459b'
        )

    def test_hash_not_string(self):
        task_runner = TaskRunner(self.TASK, self.INPUT, self.OUTPUT)
        self.assertEqual(
            task_runner._generate_key({"a": 1, "b": 2}),
            'b5da773f945631ed9943f66ab28641439d8895e350fb1fb9e21377bc63cd546bb68a5db808c57f846ddb195def323b315fe8917213'
            'aa34f996edebfa8f9653aa'
        )

    def test_get_extension_input(self):
        task_runner = TaskRunner(self.TASK, self.INPUT, self.OUTPUT)
        self.assertEqual(
            task_runner._get_extension(),
            'text/plain'
        )

    def test_execute(self):
        task_runner = TaskRunner(self.TASK, self.INPUT, self.OUTPUT)

        task_runner.execute()

        self.assertEqual(
            os.path.getsize(self.OUTPUT),
            3277
        )

