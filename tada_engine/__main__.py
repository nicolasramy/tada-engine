# -*- coding: utf-8 -*-

import argparse
import configparser
import os
import sys

from .admin import AdminService
from .master import MasterService
from .minion import MinionService


def default_configuration_filename():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'config.ini'
    )


def master_command():
    command_handler('Tada! Engine Master', MasterService)


def admin_command():
    command_handler('Tada! Engine Admin', AdminService)


def minion_command():
    command_handler('Tada! Engine Minion', MinionService)


def command_handler(name, service_class):

    parser = argparse.ArgumentParser(description=name)
    parser.add_argument('action',
                        help='start|stop|restart|status')
    parser.add_argument('--no-daemon', action='store_true',
                        help='run as a normal program')

    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read_file(open(default_configuration_filename()))

    service_instance = service_class(config, not args.no_daemon)

    if args.action in dir(service_instance):
        getattr(service_instance, args.action)()
        sys.exit(0)

    else:
        parser.print_help()
        sys.exit(2)

