# -*- coding: utf-8 -*-

import logging
import time

from .. import Service


class ProxyService(Service):
    NAME = 'cowbell-engine-proxy'

    def __init__(self, config, is_daemon):
        # Get configuration values
        pid_file = config.get('proxy', 'pid_file')
        log_file = config.get('proxy', 'log_file')

        try:
            log_level = getattr(logging, config.get('proxy', 'log_level'))
        except AttributeError:
            log_level = logging.INFO

        super(ProxyService, self).__init__(self.NAME, pid_file, log_level, log_file, is_daemon=is_daemon)

    def run(self):
        while True:
            time.sleep(3)
            self.logger.debug('eh')
