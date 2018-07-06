# -*- coding: utf-8 -*-

import atexit
import os
import logging
import logging.handlers
import time
from signal import SIGTERM
import sys

import setproctitle
from termcolor import colored

__version__ = '0.0.0'


class Messenger:
    @staticmethod
    def _write(message):
        sys.stdout.write("{}\n".format(message))

    def log(self, message):
        self._write(message)

    def info(self, message):
        self._write(colored(message, 'green'))

    def warning(self, message):
        self._write(colored(message, 'yellow'))

    def error(self, message):
        self._write(colored(message, 'red'))

    def critical(self, message):
        self._write(colored(message, 'white', 'on_red'))


class Logger:

    FORMAT = '%(asctime)s %(name)s %(levelname)s %(message)s'

    def __init__(self, name, level, output, is_daemon=True):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        formatter = logging.Formatter(self.FORMAT)

        handler = logging.FileHandler(output)
        handler.setLevel(level)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        if is_daemon:
            self.messenger = Messenger()

        else:
            self.messenger = None

            handler = logging.StreamHandler()
            handler.setLevel(level)
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)


class Service(Logger):
    """
    A generic service class.

    Usage: subclass the Service class and override the run() method
    """

    def __init__(self, name, pid_file, log_level, log_file, is_daemon=True):
        self.name = name
        self.pid_file = pid_file

        self.is_daemon = is_daemon

        self.stdin = '/dev/null'
        self.stdout = '/dev/null'
        self.stderr = '/dev/null'

        super(Service, self).__init__(name, log_level, log_file, is_daemon)

    def _write_pid_file(self, pid):

        if not os.path.exists(self.pid_file):
            open(self.pid_file, 'w+').write("{}\n".format(pid))
        else:
            message = "Unable to write pid, {} already exists".format(self.pid_file)
            if self.is_daemon:
                self.messenger.error(message)
            else:
                self.logger.error(message)
            sys.exit(3)

    def _read_pid_file(self):
        """
        Get pid from file
        """
        try:
            pid_file_resource = open(self.pid_file, 'r')
            pid = int(pid_file_resource.read().strip())
            pid_file_resource.close()
        except (ValueError, IOError):
            pid = None

        return pid

    def _remove_pid_file(self):
        try:
            os.remove(self.pid_file)
        except OSError:
            message = "Unable to remove pid_file {}"
            self.logger.warning(message.format(self.pid_file))

    def _check_pid(self):
        """
        Check pid file existence
        """
        pid = self._read_pid_file()
        return pid and os.path.exists("/proc/{}".format(pid))

    def _kill_pid(self):

        pid = self._read_pid_file()

        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except ProcessLookupError:
            self._remove_pid_file()

        except TypeError:
            if self.is_daemon:
                self.messenger.error('Service already stopped')
            else:
                self.logger.error('Service already stopped')
            sys.exit(1)

        except InterruptedError as err:
            self.logger.error(err)
            sys.exit(3)

    def processize(self):
        """
        Prepare as a simple process
        """
        atexit.register(self.stop)
        atexit.register(self._remove_pid_file)
        setproctitle.setproctitle(self.name + ' --no-daemon')

        self._write_pid_file(os.getpid())

    def daemonize(self):
        """
        Do the UNIX double-fork magic
        https://stackoverflow.com/questions/881388/what-is-the-reason-for-performing-a-double-fork-when-creating-a-daemon
        """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as e:
            self.logger.error("fork #1 failed: {} ({})".format(e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as e:
            self.logger.error("fork #2 failed: {} ({})".format(e.errno, e.strerror))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(self.stdin, 'rb')
        so = open(self.stdout, 'ab+')
        se = open(self.stderr, 'ab+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        setproctitle.setproctitle(self.name)

        # write pid_file
        atexit.register(self._remove_pid_file)
        self._write_pid_file(os.getpid())

    def start(self):
        """
        Start the service
        """
        if self._check_pid():
            message = "{} is already running".format(self.name)
            if self.is_daemon:
                self.messenger.warning(message)
            self.logger.warning(message)
            sys.exit(1)

        message = "Starting service"
        if self.is_daemon:
            self.messenger.info(message)
        self.logger.info(message)

        # Start the service
        if self.is_daemon:
            self.daemonize()
        else:
            self.processize()

        try:
            self.run()
        except KeyboardInterrupt:
            pass

    def stop(self):
        """
        Stop the service
        """
        # Try killing the Service process
        message = "Stopping service"
        if self.is_daemon:
            self.messenger.info(message)
        self.logger.info(message)
        self._kill_pid()

    def restart(self):
        """
        Restart the service
        """
        self.stop()
        self.start()

    def status(self):
        """
        Status the service
        """
        if not self.is_daemon:
            sys.exit(0)

        # Check for a pid_file to see if the service already runs
        if self._check_pid():
            message = "{} is running (PID: {})".format(self.name, self._read_pid_file())
            self.messenger.info(message)
        else:
            message = "{} is stopped".format(self.name)
            self.messenger.warning(message)
        sys.exit(1)

    def run(self):
        """
        You should override this method when you subclass Service. It will be called after the process has been
        daemonized by start() or restart().
        """
        raise NotImplementedError("Should have implemented run")
