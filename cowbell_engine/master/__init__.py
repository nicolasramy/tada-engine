# -*- coding: utf-8 -*-

import logging
import time

from .. import Service


class MasterService(Service):
    NAME = 'cowbell-engine-master'

    def __init__(self, config, is_daemon):
        # Get configuration values
        pid_file = config.get('master', 'pid_file')
        log_file = config.get('master', 'log_file')

        try:
            log_level = getattr(logging, config.get('master', 'log_level'))
        except AttributeError:
            log_level = logging.INFO

        super(MasterService, self).__init__(self.NAME, pid_file, log_level, log_file, is_daemon=is_daemon)

    def run(self):
        self.logger.info('Starting Master')
        while True:
            time.sleep(3)
            self.logger.debug('eh')
