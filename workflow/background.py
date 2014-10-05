#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2014 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-04-06
#

"""
Run background tasks
"""

from __future__ import print_function, unicode_literals

import sys
import os
import subprocess
import pickle

from workflow import Workflow

__all__ = ['is_running', 'run_in_background']

wf = Workflow()
log = wf.logger


def _arg_cache(name):
    """Return path to pickle cache file for arguments

    :param name: name of task
    :type name: ``unicode``
    :returns: Path to cache file
    :rtype: ``unicode`` filepath

    """

    return wf.cachefile('{}.argcache'.format(name))


def _pid_file(name):
    """Return path to PID file for ``name``

    :param name: name of task
    :type name: ``unicode``
    :returns: Path to PID file for task
    :rtype: ``unicode`` filepath

    """

    return wf.cachefile('{}.pid'.format(name))


def _process_exists(pid):
    """Check if a process with PID ``pid`` exists

    :param pid: PID to check
    :type pid: ``int``
    :returns: ``True`` if process exists, else ``False``
    :rtype: ``Boolean``
    """

    try:
        os.kill(pid, 0)
    except OSError:  # not running
        return False
    return True


def is_running(name):
    """
    Test whether task is running under ``name``

    :param name: name of task
    :type name: ``unicode``
    :returns: ``True`` if task with name ``name`` is running, else ``False``
    :rtype: ``Boolean``

    """
    pidfile = _pid_file(name)
    if not os.path.exists(pidfile):
        return False

    with open(pidfile, 'rb') as file_obj:
        pid = int(file_obj.read().strip())

    if _process_exists(pid):
        return True

    elif os.path.exists(pidfile):
        os.unlink(pidfile)

    return False


def _background(stdin='/dev/null', stdout='/dev/null',
                stderr='/dev/null'):  # pragma: no cover
    """Fork the current process into a background daemon.

    :param stdin: where to read input
    :type stdin: filepath
    :param stdout: where to write stdout output
    :type stdout: filepath
    :param stderr: where to write stderr output
    :type stderr: filepath

    """

    # Do first fork.
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)  # Exit first parent.
    except OSError as e:
        log.critical("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)
    # Decouple from parent environment.
    os.chdir(wf.workflowdir)
    os.umask(0)
    os.setsid()
    # Do second fork.
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)  # Exit second parent.
    except OSError as e:
        log.critical("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)
    # Now I am a daemon!
    # Redirect standard file descriptors.
    si = file(stdin, 'r', 0)
    so = file(stdout, 'a+', 0)
    se = file(stderr, 'a+', 0)
    if hasattr(sys.stdin, 'fileno'):
        os.dup2(si.fileno(), sys.stdin.fileno())
    if hasattr(sys.stdout, 'fileno'):
        os.dup2(so.fileno(), sys.stdout.fileno())
    if hasattr(sys.stderr, 'fileno'):
        os.dup2(se.fileno(), sys.stderr.fileno())


def run_in_background(name, args, **kwargs):
    """Pickle arguments to cache file, then call this script again via
    :func:`subprocess.call`.

    :param name: name of task
    :type name: ``unicode``
    :param args: arguments passed as first argument to :func:`subprocess.call`
    :param \**kwargs: keyword arguments to :func:`subprocess.call`
    :returns: exit code of sub-process
    :rtype: ``int``

    When you call this function, it caches its arguments and then calls
    ``background.py`` in a subprocess. The Python subprocess will load the
    cached arguments, fork into the background, and then run the command you
    specified.

    This function will return as soon as the ``background.py`` subprocess has
    forked, returning the exit code of *that* process (i.e. not of the command
    you're trying to run).

    If that process fails, an error will be written to the log file.

    If a process is already running under the same name, this function will
    return immediately and will not run the specified command.

    """

    if is_running(name):
        log.info('Task `{}` is already running'.format(name))
        return

    argcache = _arg_cache(name)

    # Cache arguments
    with open(argcache, 'wb') as file_obj:
        pickle.dump({'args': args, 'kwargs': kwargs}, file_obj)
        log.debug('Command arguments cached to `{}`'.format(argcache))

    # Call this script
    cmd = ['/usr/bin/python', __file__, name]
    log.debug('Calling {!r} ...'.format(cmd))
    retcode = subprocess.call(cmd)
    if retcode:  # pragma: no cover
        log.error('Failed to call task in background')
    else:
        log.debug('Executing task `{}` in background...'.format(name))
    return retcode


def main(wf):  # pragma: no cover
    """
    Load cached arguments, fork into background, then call
    :meth:`subprocess.call` with cached arguments

    """

    name = wf.args[0]
    argcache = _arg_cache(name)
    if not os.path.exists(argcache):
        log.critical('No arg cache found : {!r}'.format(argcache))
        return 1

    # Load cached arguments
    with open(argcache, 'rb') as file_obj:
        data = pickle.load(file_obj)

    # Cached arguments
    args = data['args']
    kwargs = data['kwargs']

    # Delete argument cache file
    os.unlink(argcache)

    pidfile = _pid_file(name)

    # Fork to background
    _background()

    # Write PID to file
    with open(pidfile, 'wb') as file_obj:
        file_obj.write('{}'.format(os.getpid()))

    # Run the command
    try:
        log.debug('Task `{}` running'.format(name))
        log.debug('cmd : {!r}'.format(args))

        retcode = subprocess.call(args, **kwargs)

        if retcode:
            log.error('Command failed with [{}] : {!r}'.format(retcode, args))

    finally:
        if os.path.exists(pidfile):
            os.unlink(pidfile)
        log.debug('Task `{}` finished'.format(name))


if __name__ == '__main__':  # pragma: no cover
    wf.run(main)
