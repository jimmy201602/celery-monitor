from celery import shared_task
import commands
import subprocess
import shlex
from time import sleep

@shared_task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))  #dumps its own request information
    #print commands.getoutput('ls -l')
    #print commands.getstatusoutput('la -a')

    # status = subprocess.call(['ls', '-l'])
    # print status

    # cmd = ['awk', 'length($0) > 5']
    # p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                    # stderr=subprocess.PIPE,
                    # stdin=subprocess.PIPE)
    # out, err = p.communicate('foo\nfoofoo\n')
    # print out
    # print 'err',err

    """https://stackoverflow.com/questions/4760215/running-shell-command-from-python-and-capturing-the-output/4760517"""
    #real time stdout stderr
    def runs_command(command):
        p = subprocess.Popen(command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True)
        # Read stdout from subprocess until the buffer is empty !
        for line in iter(p.stdout.readline, b''):
            if line: # Don't print blank lines
                print 'stdout',line
                # yield line
        # This ensures the process has completed, AND sets the 'returncode' attr
        while p.poll() is None:                                                                                                                                        
            sleep(.1) #Don't waste CPU-cycles
        # Empty STDERR buffer
        err = p.stderr.read()
        if p.returncode != 0:
            # The run_command() function is responsible for logging STDERR 
            print("Error traceback: " + str(err))	
        print 11111111
    print runs_command('ping -c 10 baidu.com')
    """https://stackoverflow.com/questions/89228/calling-an-external-command-in-python"""
    """https://stackoverflow.com/questions/4624416/is-there-a-possibility-to-execute-a-python-script-while-being-in-interactive-mod"""
    
    """https://stackoverflow.com/questions/163542/python-how-do-i-pass-a-string-into-subprocess-popen-using-the-stdin-argument"""