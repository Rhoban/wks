import subprocess
import os
from workspace import env, git, message, cmake

name = 'build'
help = """Runs the build"""
usage = ""
min_args = 0

def run(args):
    message.bright('* Building')

    if not os.path.exists('build'):
        os.makedirs('build')

    if subprocess.getoutput("which ninja") != '':
        cmd = 'cd build; cmake -G Ninja ..; ninja %s' % ' '.join(args)
        os.system(cmd)
    else:
        print(message.warn("Ninja was not found, you can consider: apt-get install ninja-build"))
        if input('Continue with Makefiles? (y/n) ') == 'y':
            cmd = 'cd build; cmake ..; ninja %s' % ' '.join(args)
            os.system(cmd)

    
