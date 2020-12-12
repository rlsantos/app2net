from os import system as run
from os import chdir as cd
from os import listdir
from os import getcwd as cur
from os import mkdir, rename, rmdir, remove, system
from shutil import rmtree

import subprocess

def clear():
    system('clear')

def run_command(command):
    try:
        run(command)
        return True
    except:
        return False

def run_command_w_output(command):
    try:
        output = subprocess.check_output(command, shell=True).decode('utf-8')
        return output
    except:
        return None
def popen(command):
    subprocess.Popen(command.split())

def download(url, name, dir='.'):
    try:
        run_command_w_output("wget "+url+" -O "+name)
        return True
    except:
        return False
