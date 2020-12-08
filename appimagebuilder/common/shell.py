import shlex
import subprocess
import sys
import logging


class ShellCommandError(RuntimeError):
    pass


def run_command(
    command,
    stdout=sys.stdout,
    assert_success=True,
    wait_for_completion=True,
    wait_for_completion_timeout=6000,
    **kwargs
):
    """
    Runs a command as a subprocess
    :param command: command to execute, does not need to be formatted
    :param stdout: where to pipe the standard output
    :param assert_success: should we check if the process succeeded?
    :param wait_for_completion: should we wait for completion?
    :param wait_for_completion_timeout: if yes, how much?
    :param kwargs: additional params which should be passed to format
    :return:
    """
    command = command.format(**kwargs)
    # log it
    logging.debug(command)

    # need to split the command into args
    proc = subprocess.Popen(
        shlex.split(command), stdout=stdout, stdin=sys.stdin, stderr=sys.stderr
    )

    if wait_for_completion:
        proc.wait(wait_for_completion_timeout)

    if assert_success:
        assert_command_successful_output(proc)

    # return the process instance for future use
    # if necessary
    return proc


def assert_command_successful_output(proc):
    if proc.returncode:
        raise ShellCommandError(
            '"%s" execution failed with code %s' % (proc.args, proc.returncode)
        )