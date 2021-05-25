import os
import subprocess
from colorama import Fore, Back, Style
from workspace import env, git, message, cmake

name = 'status'
help = """Shows status for projects"""
usage = ""
min_args = 0

def run(args):
  config = env.get_config(os.getcwd())

  for directory in git.get_directories():
    parts = directory.split('/')
    vendor = parts[-2]
    if config is None or vendor in config['status']:
      branch = git.branch(directory)
      message.bright("* In "+directory+" ["+message.emphasis(branch)+"]")

      status = git.status(directory).strip()
      if not status:
        print(message.success("- Everything is ok"))
      else:
        lines = status.split("\n")
        has_modified = False
        for line in lines:
          parts = line.strip().split(' ')
          if parts[0] != '??':
            has_modified = True
            break
        
        if has_modified:
          print(message.error('- Has modified files'))
        else:
          print(message.warn('- Has untracked files'))

      if git.is_ahead(directory):
        print(message.error('- Is not in sync with remote'))
        
      
  print('')
    
