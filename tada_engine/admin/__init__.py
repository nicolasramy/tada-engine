# -*- coding: utf-8 -*-

from http import HTTPStatus
import logging
from wsgiref.simple_server import make_server

import ujson

from .. import Service


class AdminService(Service):
    NAME = "tada-engine-admin"

    def __init__(self, config, is_daemon):
        # Get configuration values
        pid_file = config.get("tada-engine", "admin_pid_file")
        log_file = config.get("tada-engine", "admin_log_file")

        self.host = config.get("tada-engine", "host")
        self.admin_port = config.getint("tada-engine", "admin_port")

        try:
            log_level = getattr(logging, config.get("tada-engine", "log_level"))
        except AttributeError:
            log_level = logging.INFO

        super(AdminService, self).__init__(self.NAME, pid_file, log_level, log_file, is_daemon=is_daemon)

    @staticmethod
    def http_handler(environ, start_response):
        status = "{} {}".format(HTTPStatus.OK.value, HTTPStatus.OK.phrase)
        headers = [('Content-type', 'application/json; charset=utf-8')]  # HTTP Headers
        start_response(status, headers)

        # The returned object is going to be printed
        response = {
            "message": "Hello World"
        }
        return [bytes(ujson.dumps(response), "utf-8")]

    def run(self):
        with make_server('', self.admin_port, self.http_handler) as httpd:
            self.logger.info('Start admin on {}'.format(self.admin_port))

            # Serve until process is killed
            httpd.serve_forever()
