# -*- coding: utf-8 -*-

import configparser
import unittest

import zmq

from tada_engine.master import MasterService
from . import SAMPLE_CONFIGURATION


class MasterServiceTest(unittest.TestCase):

    @staticmethod
    def load_configuration():
        config = configparser.ConfigParser()
        config.read_string(SAMPLE_CONFIGURATION)
        return config

    @staticmethod
    def get_server_socket(config):
        context = zmq.Context()

        server_socket = context.socket(zmq.REP)
        server_socket.connect('tcp://{}:{}'.format(
            config.get('tada-engine', 'host'),
            config.get('tada-engine', 'backend_port')
        ))
        return server_socket

    @staticmethod
    def get_client_socket(config):
        context = zmq.Context()

        client_socket = context.socket(zmq.REQ)
        client_socket.connect('tcp://{}:{}'.format(
            config.get('tada-engine', 'host'),
            config.get('tada-engine', 'frontend_port')
        ))
        return client_socket

    @staticmethod
    def get_monitoring_socket(config):
        context = zmq.Context()

        monitoring_socket = context.socket(zmq.SUB)
        monitoring_socket.connect('tcp://{}:{}'.format(
            config.get('tada-engine', 'host'),
            config.get('tada-engine', 'monitoring_port')
        ))
        monitoring_socket.setsockopt(zmq.SUBSCRIBE, b"")
        return monitoring_socket

    def test_initialization(self):
        # Load configuration
        config = self.load_configuration()

        # New instance of MasterService
        master_service = MasterService(config, is_daemon=False)

        self.assertTrue(isinstance(master_service, MasterService))

    def test_monitored_queue(self):
        # Load configuration
        config = self.load_configuration()

        # New instance of MasterService
        master_service = MasterService(config, is_daemon=False)

        # Get sockets
        server_socket = self.get_server_socket(config)
        client_socket = self.get_client_socket(config)
        monitoring_socket = self.get_monitoring_socket(config)

        self.assertFalse(server_socket.closed)
        self.assertFalse(client_socket.closed)
        self.assertFalse(monitoring_socket.closed)

    # def test_monitor(self):


if __name__ == '__main__':
    unittest.main()
