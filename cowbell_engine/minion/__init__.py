# -*- coding: utf-8 -*-

import logging
import time

from .. import Service


class MinionService(Service):
    NAME = 'cowbell-engine-minion'

    def __init__(self, config, is_daemon):
        # Get configuration values
        pid_file = config.get('minion', 'pid_file')
        log_file = config.get('minion', 'log_file')

        try:
            log_level = getattr(logging, config.get('minion', 'log_level'))
        except AttributeError:
            log_level = logging.INFO

        super(MinionService, self).__init__(self.NAME, pid_file, log_level, log_file, is_daemon=is_daemon)

    def run(self):
        self.logger.info('Starting Minion')
        while True:
            time.sleep(3)
            self.logger.debug('eh')
