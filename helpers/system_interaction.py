#!/usr/bin/env python

import functools
import logging
import os
import subprocess
import sys

import helpers.dbg as dbg
import helpers.printing as print_

_LOG = logging.getLogger(__name__)


def _system(cmd, abort_on_error, suppressed_error, suppress_output, blocking,
            wrapper, output_file, dry_run, log_level):
    """

    :param cmd: string with command to execute
    :param abort_on_error: whether we should assert in case of error or not
    :param suppressed_error: set of error codes to suppress
    :param suppress_output: whether to print the output or not
    :param blocking: blocking system call or not
    :param wrapper: another command to prepend the execution of cmd
    :param output_file: redirect stdout and stderr to this file
    :param dry_run: just print the final command but not execute it
    :param log_level: print the command to execute at level "log_level"
    :return: return code (int), output of the command (str)
    """
    # Prepare the command line.
    cmd = "(%s)" % cmd
    if output_file is not None:
        dir_name = os.path.dirname(output_file)
        if not os.path.exists(dir_name):
            _LOG.debug("'%s' doesn't exist: creating", dir_name)
            os.makedirs(dir_name)
        cmd += " >%s" % output_file
    cmd += " 2>&1"
    if wrapper:
        cmd = wrapper + " && " + cmd
    _LOG.log(log_level, "> %s", cmd)
    #
    output = ""
    if dry_run:
        _LOG.warning("Not executing cmd\n%s\nas per user request", cmd)
        rc = 0
        return rc, output
    # Execute the command.
    try:
        stdout = subprocess.PIPE
        stderr = subprocess.STDOUT
        p = subprocess.Popen(
            cmd,
            shell=True,
            executable="/bin/bash",
            stdout=stdout,
            stderr=stderr)
        output = ""
        if blocking:
            # Blocking.
            while True:
                line = p.stdout.readline().decode("utf-8")
                if not line:
                    break
                if not suppress_output:
                    print((line.rstrip("\n")))
                output += line
            p.stdout.close()
            rc = p.wait()
        else:
            # Not blocking.
            rc = 0
        if suppressed_error is not None:
            dbg.dassert_isinstance(suppressed_error, set)
            if rc in suppressed_error:
                rc = 0
    except OSError:
        rc = -1
    _LOG.debug("rc=%s", rc)
    if abort_on_error and rc != 0:
        msg = ("\n" + print_.frame("cmd='%s' failed with rc='%s'" % (cmd, rc)) +
               "\nOutput of the failing command is:\n%s\n%s\n%s" %
               (print_.line(">"), output, print_.line("<")))
        _LOG.error("%s", msg)
        raise RuntimeError("cmd='%s' failed with rc='%s'" % (cmd, rc))
    #dbg.dassert_type_in(output, (str, ))
    return rc, output


def system(cmd,
           abort_on_error=True,
           suppressed_error=None,
           suppress_output=True,
           blocking=True,
           wrapper=None,
           output_file=None,
           dry_run=False,
           log_level=logging.DEBUG):
    rc, _ = _system(
        cmd,
        abort_on_error=abort_on_error,
        suppressed_error=suppressed_error,
        suppress_output=suppress_output,
        blocking=blocking,
        wrapper=wrapper,
        output_file=output_file,
        dry_run=dry_run,
        log_level=log_level)
    return rc


def system_to_string(cmd,
                     abort_on_error=True,
                     wrapper=None,
                     dry_run=False,
                     log_level=logging.DEBUG):
    rc, output = _system(
        cmd,
        abort_on_error=abort_on_error,
        suppressed_error=None,
        suppress_output=True,
        # If we want to see the output the system call must be blocking.
        blocking=True,
        wrapper=wrapper,
        output_file=None,
        dry_run=dry_run,
        log_level=log_level)
    output = output.rstrip("\n")
    return rc, output


@functools.lru_cache(maxsize=None)
def get_user_name():
    return system_to_string("whoami")[1]


@functools.lru_cache(maxsize=None)
def get_server_name():
    return system_to_string("uname -n")[1]


@functools.lru_cache(maxsize=None)
def get_os_name():
    return system_to_string("uname -s")[1]


def query_yes_no(question, abort_on_no=True):
    """
    Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {
        "yes": True,
        "y": True,
        #
        "no": False,
        "n": False
    }
    prompt = " [y/n] "
    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if choice in valid:
            ret = valid[choice]
            break
    _LOG.debug("ret=%s", ret)
    if abort_on_no:
        if not ret:
            print("You answer no: exiting")
            sys.exit(-1)
    return ret
