# -*- coding: utf-8 -*-

import argparse
import configparser
import os
import sys

from .master import MasterService
from .minion import MinionService
from .proxy import ProxyService


def default_configuration_filename():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'config.ini'
    )


def master_command():
    command_handler('Tada! Engine Master', MasterService)


def minion_command():
    command_handler('Tada! Engine Minion', MinionService)


def proxy_command():
    command_handler('Tada! Engine Proxy', ProxyService)


def command_handler(name, service_class):

    parser = argparse.ArgumentParser(description=name)
    parser.add_argument('action',
                        help='start|stop|restart|status')
    parser.add_argument('--no-daemon', action='store_true',
                        help='run as a normal program')

    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read_file(open(default_configuration_filename()))

    proxy_instance = service_class(config, not args.no_daemon)

    if args.action in dir(proxy_instance):
        getattr(proxy_instance, args.action)()
        sys.exit(0)

    else:
        parser.print_help()
        sys.exit(2)

