# -*- coding: utf-8 -*-

import atexit
import os
import time
from signal import SIGTERM
import sys

import setproctitle

__version__ = '0.0.0'


def write_pid_file(pid_file, pid):
    if not os.path.exists(pid_file):
        open(pid_file, 'w+').write("{}\n".format(pid))


def read_pid_file(pid_file):
    """
    Get pid from file
    :param pid_file:
    :return:
    """
    try:
        pid_file_resource = open(pid_file, 'r')
        pid = int(pid_file_resource.read().strip())
        pid_file_resource.close()
    except IOError:
        pid = None

    return pid


def remove_pid_file(pid_file):
    try:
        os.remove(pid_file)
    except OSError:
        message = "Unable to remove pid_file %s\n"
        sys.stderr.write(message % pid_file)


def check_pid(pid_file, raise_exit=False):
    """
    Check pid file existence
    :param pid_file:
    :param raise_exit:
    :return:
    """
    pid = read_pid_file(pid_file)
    if pid and os.path.exists("/proc/{}".format(pid)):
        if raise_exit:
            message = "pid_file %s already exist. Service already running?\n"
            sys.stderr.write(message % pid_file)
            sys.exit(1)


def kill_pid(pid_file):

    pid = read_pid_file(pid_file)
    status = 0

    try:
        while 1:
            os.kill(pid, SIGTERM)
            time.sleep(0.1)
    except ProcessLookupError:
        remove_pid_file(pid_file)

    except InterruptedError as err:
        print(err)
        status = 3

    finally:
        sys.exit(status)


class Program:
    """
    A generic program class.

    Usage: subclass the Program class and override the run() method
    """

    def __init__(self, name, pid_file, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.name = name + ' --no-daemon'
        self.pid_file = pid_file

        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    def start(self):
        check_pid(self.pid_file)

        atexit.register(self.stop)
        setproctitle.setproctitle(self.name)

        write_pid_file(self.pid_file, os.getpid())

        # Start the program
        self.run()

    def stop(self):
        # Try killing the Program process
        kill_pid(self.pid_file)

    def run(self):
        """
        You should override this method when you subclass Program. It will be called after the process has been
        started by start().
        """
        raise NotImplementedError("Should have implemented run")


class Service:
    """
    A generic service class.

    Usage: subclass the Service class and override the run() method
    """

    def __init__(self, name, pid_file, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.name = name
        self.pid_file = pid_file

        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

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
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
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
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
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
        atexit.register(remove_pid_file, self.pid_file)
        write_pid_file(self.pid_file, os.getpid())

    def start(self):
        """
        Start the service
        """
        check_pid(self.pid_file)

        # Start the service
        self.daemonize()
        self.run()

    def stop(self):
        """
        Stop the service
        """
        # Try killing the Service process
        kill_pid(self.pid_file)

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
        # Check for a pid_file to see if the service already runs
        pid = read_pid_file(self.pid_file)

        check_pid(self.pid_file, True)

        if pid:
            message = "pid_file %s is running.\n"
        else:
            message = "pid_file %s is stopped.\n"

        sys.stderr.write(message % self.pid_file)
        sys.exit(1)

    def run(self):
        """
        You should override this method when you subclass Service. It will be called after the process has been
        daemonized by start() or restart().
        """
        raise NotImplementedError("Should have implemented run")
