#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-04-01
#

"""
"""

from __future__ import print_function, absolute_import

import atexit
from contextlib import contextmanager
import logging
import os
import signal
import subprocess
import sys
import time

RUN_FOR = 10  # seconds

HERE = os.path.dirname(__file__)
LOGFILE = os.path.join(HERE, 'daemon.log')
PIDFILE = os.path.join(HERE, 'daemon.pid')

logging.basicConfig(
    filename=LOGFILE,
    format='%(levelname)-8s %(message)s',
    level=logging.DEBUG,
)
log = logging.getLogger(__name__)

# Possible fixes
# TODO: use os._exit(), not sys.exit()
# Close file descriptors
# Add an exec


class PidFile(object):

    def __init__(self, path):
        self.path = path

    def __enter__(self):
        with open(self.path, 'wb') as fp:
            fp.write(str(os.getpid()))
        log.debug('[pidfile] saved PID (%d) to %s', os.getpid(), self.path)
        signal.signal(signal.SIGTERM, self.quit)
        atexit.register(self.remove)
        return self

    def __exit__(self, typ, value, traceback):
        self.remove()

    def quit(self, signum, frame):
        log.debug('[pidfile] caught signal %d', signum)
        raise SystemExit('caught signal {0}'.format(signum))

    def remove(self):
        try:
            os.unlink(self.path)
            log.debug('[pidfile] deleted %s', self.path)
        except (OSError, IOError) as err:
            if err.errno != 2:
                raise err


@contextmanager
def pidfile(p):
    """Write PID to file ``p``."""
    def rm():
        os.unlink(p)
        log.debug('[daemon] removed PID file')

    def quit(signum, frame):
        log.debug('[daemon] caught signal %d', signum)
        raise SystemExit('terminating for signal %d', signum)

    with open(p, 'wb') as fp:
        fp.write(str(os.getpid()))

    atexit.register(rm)
    signal.signal(signal.SIGTERM, quit)
    # signal.signal(signal.SIGABRT, rm)
    yield
    rm


def _fork_and_exit_parent(errmsg):
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as err:
        log.critical('[daemon] %s: (%d) %s', errmsg, err.errno, err.strerror)
        raise err


def daemonise(stdin='/dev/null', stdout='/dev/null',
              stderr='/dev/null'):  # pragma: no cover
    """Fork the current process into a background daemon.

    :param stdin: where to read input
    :type stdin: filepath
    :param stdout: where to write stdout output
    :type stdout: filepath
    :param stderr: where to write stderr output
    :type stderr: filepath

    """
    pid = os.getpid()
    log.info('[daemon] parent   (pid=%d, gid=%d, sid=%d)',
             pid, os.getpgid(pid), os.getsid(pid))

    _fork_and_exit_parent('fork #1 failed')

    pid = os.getpid()
    log.info('[daemon] fork#1   (pid=%d, gid=%d, sid=%d)',
             pid, os.getpgid(pid), os.getsid(pid))

    # Decouple from parent environment.
    os.chdir(HERE)
    # os.umask(077)
    os.setsid()

    pid = os.getpid()
    log.info('[daemon] decouple (pid=%d, gid=%d, sid=%d)',
             pid, os.getpgid(pid), os.getsid(pid))

    _fork_and_exit_parent('fork #2 failed')

    pid = os.getpid()
    log.info('[daemon] fork#2   (pid=%d, gid=%d, sid=%d)',
             pid, os.getpgid(pid), os.getsid(pid))

    # Now I am a daemon!
    # Redirect standard file descriptors.
    si = open(stdin, 'r', 0)
    so = open(stdout, 'a+', 0)
    se = open(stderr, 'a+', 0)

    if hasattr(sys.stdin, 'fileno'):
        log.debug('[daemon] STDIN  connected to %s (fileno=%d)',
                  stdin, sys.stdin.fileno())
        os.dup2(si.fileno(), sys.stdin.fileno())
    if hasattr(sys.stdout, 'fileno'):
        log.debug('[daemon] STDOUT connected to %s (fileno=%d)',
                  stdout, sys.stdout.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
    if hasattr(sys.stderr, 'fileno'):
        log.debug('[daemon] STDERR connected to %s (fileno=%d)',
                  stderr, sys.stderr.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())


def start_runner():
    """Start daemon in another process."""
    print('[runner] starting daemon ...')
    cmd = ['/usr/bin/python', __file__, '--daemon']
    code = subprocess.call(cmd)
    if code == 2:
        print('[runner] daemon already running')
    elif code:
        print('[runner] error starting daemon (daemon exited with %d)' % code)
    else:
        print('[runner] daemon successfully started')
    return code


def stop_daemon():
    """Send SIGTERM to daemon."""
    if not os.path.exists(PIDFILE):
        print('[runner] daemon is not running')
        return 1

    with open(PIDFILE) as fp:
        pid = int(fp.read())

    try:
        os.kill(pid, signal.SIGTERM)
    except OSError as err:
        if err.errno == 3:
            print('[runner] daemon not running')
            if os.path.exists(PIDFILE):
                os.unlink(PIDFILE)
                print('[runner] deleted stale PID file')
            return 0

        else:
            raise err

    print('[runner] sent SIGTERM to daemon')


def start_daemon():
    """Start daemon."""
    log.info('-' * 30)
    if os.path.exists(PIDFILE):
        log.critical('[daemon] PID file exists: %s', PIDFILE)
        return 2

    log.info('[daemon] moving to background ...')

    try:
        daemonise()

        with PidFile(PIDFILE):
            pid = os.getpid()
            log.info('[daemon] running in background ...')
            log.info('[daemon] pid=%d, gid=%d, sid=%d',
                     pid, os.getpgid(pid), os.getsid(pid))
            for i in range(1, RUN_FOR):
                log.info('[daemon] exiting in %ds ...', RUN_FOR - i)
                time.sleep(1)

    except Exception as err:
        log.critical(err, exc_info=True)
        return 1

    finally:
        log.info('[daemon] exiting')


def main():
    """Run runner or daemon."""
    args = sys.argv[1:]
    if args:
        if args[0] == '--daemon':
            return start_daemon()
        elif args[0] == '--stop':
            return stop_daemon()

    return start_runner()


if __name__ == '__main__':
    sys.exit(main())
