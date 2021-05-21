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
  
  cmd = 'cd build; cmake ..; make %s' % ' '.join(args)
  os.system(cmd)
  