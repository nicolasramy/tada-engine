# -*- coding: utf-8 -*-

# TODO: ConfigParser -- https://docs.python.org/3/library/configparser.html

import argparse
import sys

from .master import MasterProgram, MasterService
from .minion import MinionProgram, MinionService
from .proxy import ProxyProgram, ProxyService


def master_command():
    parser = argparse.ArgumentParser(description='Cowbell Engine Master')
    parser.add_argument('action',
                        help='start|stop|restart|status')
    parser.add_argument('--no-daemon', action='store_true',
                        help='run as a normal program')

    args = parser.parse_args()

    proxy_instance = MasterProgram() if args.no_daemon else MasterService()

    if args.action in dir(proxy_instance):
        getattr(proxy_instance, args.action)()
        sys.exit(0)

    else:
        parser.print_help()
        sys.exit(2)


def minion_command():
    parser = argparse.ArgumentParser(description='Cowbell Engine Minion')
    parser.add_argument('action',
                        help='start|stop|restart|status')
    parser.add_argument('--no-daemon', action='store_true',
                        help='run as a normal program')

    args = parser.parse_args()

    proxy_instance = MinionProgram() if args.no_daemon else MinionService()

    if args.action in dir(proxy_instance):
        getattr(proxy_instance, args.action)()
        sys.exit(0)

    else:
        parser.print_help()
        sys.exit(2)


def proxy_command():
    parser = argparse.ArgumentParser(description='Cowbell Engine Proxy')
    parser.add_argument('action',
                        help='start|stop|restart|status')
    parser.add_argument('--no-daemon', action='store_true',
                        help='run as a normal program')

    args = parser.parse_args()

    proxy_instance = ProxyProgram() if args.no_daemon else ProxyService()

    if args.action in dir(proxy_instance):
        getattr(proxy_instance, args.action)()
        sys.exit(0)

    else:
        parser.print_help()
        sys.exit(2)
