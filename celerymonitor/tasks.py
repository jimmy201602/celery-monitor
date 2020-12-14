from celery import shared_task
import subprocess
from time import sleep
try:
    from .extend_tasks import *
except ImportError:
    pass


@shared_task(bind=True)
def debug_task(self):
    # dumps its own request information
    print('Request: {0!r}'.format(self.request))

    """https://stackoverflow.com/questions/4760215/running-shell-command-from-python-and-capturing-the-output/4760517"""
    # real time stdout stderr
    def runs_command(command):
        p = subprocess.Popen(command,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             shell=True)
        # Read stdout from subprocess until the buffer is empty !
        for line in iter(p.stdout.readline, b''):
            if line:  # Don't print blank lines
                print 'stdout', line
                # yield line
        # This ensures the process has completed, AND sets the 'returncode' attr
        while p.poll() is None:
            sleep(.1)  # Don't waste CPU-cycles
        # Empty STDERR buffer
        err = p.stderr.read()
        if p.returncode != 0:
            # The run_command() function is responsible for logging STDERR
            print("Error traceback: " + str(err))
    print runs_command('ping -c 10 baidu.com')
    """https://stackoverflow.com/questions/89228/calling-an-external-command-in-python"""
    """https://stackoverflow.com/questions/4624416/is-there-a-possibility-to-execute-a-python-script-while-being-in-interactive-mod"""

    """https://stackoverflow.com/questions/163542/python-how-do-i-pass-a-string-into-subprocess-popen-using-the-stdin-argument"""
